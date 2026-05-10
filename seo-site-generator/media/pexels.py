import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OUTPUT_DIR = Path("output/images")


def search_image(query: str) -> dict | None:
    if not PEXELS_API_KEY:
        raise ValueError("PEXELS_API_KEY not set in .env")

    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": 5, "orientation": "landscape"},
        timeout=15,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    return photos[0] if photos else None


def download_image(photo: dict, service: str, city: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", f"{service} {city}".lower()).strip("-")
    filename = OUTPUT_DIR / f"{slug}.jpg"

    url = photo["src"]["large2x"]
    resp = requests.get(url, timeout=30, stream=True)
    resp.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return filename


def fetch_image(query: str, service: str, city: str) -> Path | None:
    photo = search_image(query)
    if not photo:
        return None
    return download_image(photo, service, city)
