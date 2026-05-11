"""
Technical Test — Rank & Rent SEO Automation
Niche : Stamped Concrete Patios
City  : Farmington Hills, MI

Requirements:
  - Gemini 2.0 Flash content generation
  - Structured JSON output (title_tag, meta_description, h1, content_html)
  - 800+ words, 2+ real local landmarks
  - WordPress REST API push as Draft (Application Password auth)

Usage:
  pip install google-generativeai requests python-dotenv
  Set env vars (or create .env):
    GEMINI_API_KEY=...
    WP_URL=https://yoursite.com
    WP_USERNAME=admin
    WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
  python concrete_test.py
"""

import json
import os
import re
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────

KEYWORD  = "Stamped Concrete Patios"
CITY     = "Farmington Hills, MI"
SLUG     = "stamped-concrete-patios-farmington-hills-mi"

GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")
WP_URL          = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME     = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# ── Prompt ─────────────────────────────────────────────────────────────────────

PROMPT = """
You are an expert local SEO copywriter. Generate a complete, high-converting service page.

Service : Stamped Concrete Patios
City    : Farmington Hills, MI
Target keyword: "Stamped Concrete Patios Farmington Hills"

IMPORTANT LOCAL SEO REQUIREMENT:
You MUST naturally mention at least two of these real Farmington Hills landmarks or streets
in the body content to demonstrate local relevancy:
- Heritage Park (11 Mile Rd & Farmington Rd)
- Orchard Lake Road
- Grand River Avenue
- Twelve Mile Road
- Costick Activities Center
- Farmington Hills City Hall

Return ONLY a valid JSON object with this exact structure:
{
  "title_tag": "...",
  "meta_description": "...",
  "h1": "...",
  "content_html": "..."
}

Rules:
- title_tag: include keyword + city signal, MUST be under 60 characters
- meta_description: high-CTR, include keyword + call to action, MUST be under 155 characters
- h1: must contain "Stamped Concrete Patios" and "Farmington Hills"
- content_html: clean HTML with H2s, H3s, and bullet points — MINIMUM 800 words.
  Structure:
    <h2>Why Stamped Concrete Patios Are Perfect for Farmington Hills Homes</h2>
    <h2>Our Stamped Concrete Design Options</h2>
    <h3>Popular Patterns</h3>  (bullet list)
    <h2>The Installation Process</h2>
    <h2>Serving Farmington Hills and Oakland County</h2>  ← mention landmarks here
    <h2>Frequently Asked Questions</h2>
    <h3>How much does a stamped concrete patio cost in Farmington Hills?</h3>
    <h3>How long does installation take?</h3>
    <h3>Do you serve areas near Orchard Lake Road?</h3>
    <p>Strong CTA paragraph at the end</p>
"""

# ── Step 1: Generate content with Gemini 2.0 Flash ────────────────────────────

def generate_content() -> dict:
    print("Calling Gemini 2.0 Flash...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=PROMPT,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    data = json.loads(text)

    # Validate requirements
    assert len(data["title_tag"]) <= 60, \
        f"title_tag too long: {len(data['title_tag'])} chars"
    assert len(data["meta_description"]) <= 155, \
        f"meta_description too long: {len(data['meta_description'])} chars"
    assert "Farmington Hills" in data["h1"], \
        "H1 must contain 'Farmington Hills'"

    word_count = len(re.sub(r"<[^>]+>", " ", data["content_html"]).split())
    assert word_count >= 800, f"content_html too short: {word_count} words"

    landmarks = ["Heritage Park", "Orchard Lake", "Grand River", "Twelve Mile",
                 "Costick", "Farmington Hills City Hall"]
    found = [lm for lm in landmarks if lm.lower() in data["content_html"].lower()]
    assert len(found) >= 2, f"Need 2+ local landmarks, found: {found}"

    print(f"  title_tag       : {data['title_tag']} ({len(data['title_tag'])} chars)")
    print(f"  meta_description: {data['meta_description']} ({len(data['meta_description'])} chars)")
    print(f"  h1              : {data['h1']}")
    print(f"  word_count      : ~{word_count} words")
    print(f"  local landmarks : {found}")
    return data


# ── Step 2: Push to WordPress as Draft ────────────────────────────────────────

def push_to_wordpress(data: dict) -> dict:
    print("\nPushing to WordPress...")

    endpoint = f"{WP_URL}/wp-json/wp/v2/pages"
    auth     = HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)

    payload = {
        "title"   : data["h1"],
        "slug"    : SLUG,
        "content" : data["content_html"],
        "excerpt" : data["meta_description"],
        "status"  : "draft",
        "meta"    : {
            "rank_math_title"            : data["title_tag"],
            "rank_math_description"      : data["meta_description"],
            "_yoast_wpseo_title"         : data["title_tag"],
            "_yoast_wpseo_metadesc"      : data["meta_description"],
        },
    }

    resp = requests.post(endpoint, json=payload, auth=auth, timeout=30)
    resp.raise_for_status()
    page = resp.json()

    print(f"  Status : {page.get('status')}")
    print(f"  Link   : {page.get('link')}")
    print(f"  Edit   : {WP_URL}/wp-admin/post.php?post={page.get('id')}&action=edit")
    return page


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Rank & Rent SEO Automation — Technical Test")
    print(f"Niche: {KEYWORD} | City: {CITY}")
    print("=" * 60)

    data = generate_content()

    print("\nGenerated JSON:")
    print(json.dumps({k: v[:80] + "..." if k == "content_html" else v
                      for k, v in data.items()}, indent=2))

    if WP_URL and WP_USERNAME and WP_APP_PASSWORD:
        page = push_to_wordpress(data)
        print("\nDone! Open the edit link above to view the draft in WordPress.")
    else:
        print("\nWP credentials not set — skipping WordPress push.")
        print("Set WP_URL, WP_USERNAME, WP_APP_PASSWORD in .env to deploy.")

        with open("output_concrete_test.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Full JSON saved to output_concrete_test.json")
