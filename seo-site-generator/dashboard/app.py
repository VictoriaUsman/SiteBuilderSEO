import asyncio
import io
import os
import uuid
from pathlib import Path

import pandas as pd
from dotenv import set_key
from fastapi import FastAPI, File, Form, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AI SEO Site Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="dashboard/templates")

FRONTEND_DIST = Path("frontend/dist")

# In-memory store
jobs: dict[str, dict] = {}
job_sockets: dict[str, list[WebSocket]] = {}

ENV_FILE = Path(".env")


# ── REST endpoints ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "jobs": list(jobs.values())})


@app.get("/api/jobs")
async def list_jobs():
    return list(jobs.values())


@app.post("/generate")
async def generate(
    csv_file: UploadFile = File(...),
    domain: str = Form(...),
    provider: str = Form("gemini"),
    status: str = Form("draft"),
    post_type: str = Form("posts"),
    dry_run: str = Form("false"),
    # Per-user credential overrides (from browser localStorage)
    WP_ACCESS_TOKEN: str = Form(""),
    WP_SITE: str = Form(""),
    WP_URL: str = Form(""),
    WP_USERNAME: str = Form(""),
    WP_APP_PASSWORD: str = Form(""),
    GEMINI_API_KEY: str = Form(""),
    OPENAI_API_KEY: str = Form(""),
    PEXELS_API_KEY: str = Form(""),
):
    job_id = str(uuid.uuid4())[:8]
    content = await csv_file.read()
    df = pd.read_csv(io.StringIO(content.decode()))
    rows = df.fillna("").to_dict(orient="records")

    # Build credential dict — user values take priority over server env
    creds = {
        "WP_ACCESS_TOKEN": WP_ACCESS_TOKEN or os.getenv("WP_ACCESS_TOKEN", ""),
        "WP_SITE": WP_SITE or os.getenv("WP_SITE", ""),
        "WP_URL": WP_URL or os.getenv("WP_URL", ""),
        "WP_USERNAME": WP_USERNAME or os.getenv("WP_USERNAME", ""),
        "WP_APP_PASSWORD": WP_APP_PASSWORD or os.getenv("WP_APP_PASSWORD", ""),
        "GEMINI_API_KEY": GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", ""),
        "OPENAI_API_KEY": OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", ""),
        "PEXELS_API_KEY": PEXELS_API_KEY or os.getenv("PEXELS_API_KEY", ""),
    }

    is_dry = dry_run.lower() in ("true", "1", "yes")
    jobs[job_id] = {"id": job_id, "domain": domain, "status": "running", "logs": [], "pages": []}
    job_sockets[job_id] = []

    asyncio.create_task(_run_job(job_id, rows, domain, provider, status, post_type, is_dry, creds))

    return JSONResponse({"job_id": job_id, "message": f"Job {job_id} started"})


@app.get("/jobs/{job_id}")
async def job_status(job_id: str):
    if job_id not in jobs:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return jobs[job_id]


@app.post("/api/settings")
async def save_settings(request: Request):
    data: dict = await request.json()
    ENV_FILE.touch(exist_ok=True)
    for key, value in data.items():
        if value:
            set_key(str(ENV_FILE), key, value)
    return {"ok": True}


# ── WebSocket ──────────────────────────────────────────────────────────────────

@app.websocket("/ws/{job_id}")
async def ws_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    if job_id not in job_sockets:
        job_sockets[job_id] = []
    job_sockets[job_id].append(websocket)

    # Send current state immediately
    if job_id in jobs:
        await websocket.send_json(jobs[job_id])

    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        job_sockets[job_id].remove(websocket)


async def _broadcast(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return
    dead = []
    for ws in job_sockets.get(job_id, []):
        try:
            await ws.send_json(job)
        except Exception:
            dead.append(ws)
    for ws in dead:
        job_sockets[job_id].remove(ws)


# ── Job runner ─────────────────────────────────────────────────────────────────

async def _run_job(job_id: str, rows: list[dict], domain: str, provider: str, status: str, post_type: str, dry_run: bool, creds: dict = {}):
    from generators.async_generator import generate_pages_async
    from seo.validator import validate_page
    from seo.linking import InternalLinkGraph

    job = jobs[job_id]

    def log(msg: str):
        job["logs"].append(msg)

    try:
        log(f"Generating {len(rows)} pages...")
        await _broadcast(job_id)

        results = await generate_pages_async(rows, domain, provider,
                                              gemini_key=creds.get("GEMINI_API_KEY"),
                                              openai_key=creds.get("OPENAI_API_KEY"))

        graph = InternalLinkGraph()
        for r in results:
            row, content = r["row"], r.get("content", {})
            if content:
                graph.add_page(
                    content.get("slug", ""),
                    row.get("service", ""),
                    row.get("city", ""),
                    row.get("keyword", ""),
                )
        graph.build_links()

        if not dry_run:
            from wordpress.client import WordPressClient
            client = WordPressClient(
                url=creds.get("WP_URL"),
                username=creds.get("WP_USERNAME"),
                app_password=creds.get("WP_APP_PASSWORD"),
                access_token=creds.get("WP_ACCESS_TOKEN"),
                site=creds.get("WP_SITE"),
            )
            if not client.test_connection():
                log("ERROR: WordPress connection failed")
                job["status"] = "failed"
                await _broadcast(job_id)
                return

        for r in results:
            row, content = r["row"], r.get("content", {})
            if not content:
                continue

            vr = validate_page(content, row.get("keyword", ""))
            slug = content.get("slug", "?")
            content["internal_link_suggestions"] = graph.get_links_for(slug)

            if not dry_run:
                from media.pexels import fetch_image
                from wordpress.media import upload_image
                from wordpress.pages import create_page

                img_path = fetch_image(
                    content.get("image_search_query", ""),
                    row.get("service", ""),
                    row.get("city", ""),
                    api_key=creds.get("PEXELS_API_KEY"),
                )
                media_id = upload_image(client, img_path, content.get("image_alt_text", "")) if img_path else None
                page = create_page(client, content, media_id, domain, status=status, post_type=post_type)
                url = page.get("link", slug)
            else:
                url = f"https://{domain}/{slug}"

            log(f"{'PASS' if vr.passed else 'WARN'} {slug}")
            job["pages"].append({"slug": slug, "url": url, "valid": vr.passed, "content": content})
            await _broadcast(job_id)

        job["status"] = "done"
        log(f"Complete: {len(job['pages'])} pages")
        await _broadcast(job_id)

    except Exception as e:
        job["status"] = "failed"
        job["logs"].append(f"ERROR: {e}")
        await _broadcast(job_id)


# ── Serve React frontend (must be last) ────────────────────────────────────────

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def serve_react(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")
