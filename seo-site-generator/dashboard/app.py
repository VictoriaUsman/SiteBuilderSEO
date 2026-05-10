import asyncio
import io
import os
import uuid
from pathlib import Path

import pandas as pd
from dotenv import set_key, dotenv_values
from fastapi import FastAPI, File, Form, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AI SEO Site Builder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="dashboard/templates")

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
):
    job_id = str(uuid.uuid4())[:8]
    content = await csv_file.read()
    df = pd.read_csv(io.StringIO(content.decode()))
    rows = df.fillna("").to_dict(orient="records")

    is_dry = dry_run.lower() in ("true", "1", "yes")
    jobs[job_id] = {"id": job_id, "domain": domain, "status": "running", "logs": [], "pages": []}
    job_sockets[job_id] = []

    asyncio.create_task(_run_job(job_id, rows, domain, provider, status, post_type, is_dry))

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

async def _run_job(job_id: str, rows: list[dict], domain: str, provider: str, status: str, post_type: str, dry_run: bool):
    from generators.async_generator import generate_pages_async
    from seo.validator import validate_page
    from seo.linking import InternalLinkGraph

    job = jobs[job_id]

    def log(msg: str):
        job["logs"].append(msg)

    try:
        log(f"Generating {len(rows)} pages...")
        await _broadcast(job_id)

        results = await generate_pages_async(rows, domain, provider)

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
            client = WordPressClient()
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
