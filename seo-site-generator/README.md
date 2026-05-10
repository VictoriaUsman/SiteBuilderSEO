# AI Local SEO Site Builder

A Python automation engine that generates and publishes local SEO pages to WordPress at scale. Upload a keyword CSV, generate AI-written content via Gemini or OpenAI, and publish directly to WordPress.com or self-hosted WordPress — with a React dashboard to manage everything.

## Features

- **AI content generation** — Gemini or OpenAI writes SEO-optimized title tags, meta descriptions, H1, H2 sections, FAQ, and CTAs
- **WordPress publishing** — supports both WordPress.com (OAuth) and self-hosted WordPress.org (Application Passwords)
- **Pexels image automation** — searches, downloads, renames, and uploads SEO-named featured images
- **Internal link graph** — automatically connects pages by service and city using NetworkX
- **SEO QA validator** — checks keyword in H1, title/meta length, slug format, word count, duplicate detection
- **Async generation** — generates up to 10 pages concurrently
- **React dashboard** — drag-and-drop CSV upload, inline editor, live per-page progress, content preview modal, force-directed link graph
- **Config-driven deployments** — run an entire site from a single YAML file

## Stack

| Layer | Tech |
|---|---|
| Content generation | Google Gemini 1.5 Flash / OpenAI GPT-4o mini |
| Backend | Python, FastAPI, pandas |
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| WordPress | REST API (wp/v2) — WordPress.com OAuth or self-hosted Basic Auth |
| Images | Pexels API |
| Link graph | NetworkX |
| Realtime | WebSocket |

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/VictoriaUsman/SiteBuilderSEO.git
cd SiteBuilderSEO/seo-site-generator

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
# AI — pick one
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...
AI_PROVIDER=gemini

# WordPress.com (OAuth)
WP_ACCESS_TOKEN=your_token
WP_SITE=yoursite.wordpress.com

# OR self-hosted WordPress.org
# WP_URL=https://yoursite.com
# WP_USERNAME=admin
# WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Images
PEXELS_API_KEY=your_key
```

### 3. Run the dashboard

```bash
# Terminal 1 — backend
uvicorn dashboard.app:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

## Dashboard

| Page | What it does |
|---|---|
| **Generate** | 3-step wizard: upload CSV → configure → generate & publish |
| **Jobs** | History of all runs with expandable logs and page results |
| **Settings** | Set API keys and WordPress credentials (saves to `.env`) |

The Generate page includes:
- Drag-and-drop CSV upload or inline editor (add/edit/delete rows before running)
- Per-page live progress via WebSocket
- Click any completed page to preview title, meta, H1, body, FAQ, and internal links before it publishes
- Force-directed internal link graph that updates as pages complete

## CLI Usage

```bash
# Generate and publish from a CSV
python main.py --csv configs/sample_keywords.csv --domain example.com

# Dry run — generate content but skip WordPress upload
python main.py --csv configs/sample_keywords.csv --domain example.com --dry-run

# Choose AI provider
python main.py --csv configs/sample_keywords.csv --domain example.com --provider openai

# Publish as drafts
python main.py --csv configs/sample_keywords.csv --domain example.com --status draft
```

## Config-Driven Deployments

Create a YAML config per site and run the whole thing with one command:

```bash
python build_site.py configs/example.yaml
python build_site.py configs/example.yaml --dry-run
```

Example config (`configs/example.yaml`):

```yaml
site:
  domain: bestroofingdallas.com
  city: Dallas
  service: Roof Repair

wordpress:
  url: https://bestroofingdallas.com
  username: admin
  app_password: "xxxx xxxx xxxx xxxx xxxx xxxx"

ai:
  provider: gemini

publishing:
  status: publish
  create_parent_page: true

csv_file: configs/dallas_roofing.csv
```

## CSV Format

```csv
keyword,city,service
roof repair,Dallas,Roof Repair
emergency roofing,Dallas,Emergency Roofing
plumber,Austin,Plumbing Services
```

## Project Structure

```
seo-site-generator/
├── generators/
│   ├── content_generator.py   # Gemini + OpenAI content generation
│   └── async_generator.py     # Concurrent page generation with semaphore
├── wordpress/
│   ├── client.py              # REST API client (WordPress.com + self-hosted)
│   ├── pages.py               # Page/post creation with HTML body builder
│   └── media.py               # Image upload to WP media library
├── seo/
│   ├── validator.py           # SEO QA checks (H1, meta length, slug, word count)
│   └── linking.py             # Internal link graph with NetworkX
├── media/
│   └── pexels.py              # Pexels image search and download
├── prompts/
│   └── templates.py           # AI prompt templates and schema markup
├── dashboard/
│   └── app.py                 # FastAPI backend with WebSocket
├── frontend/
│   └── src/                   # React + TypeScript dashboard
├── configs/
│   ├── example.yaml           # Sample site config
│   └── sample_keywords.csv    # Sample keyword CSV
├── tests/
│   ├── test_validator.py
│   └── test_linking.py
├── main.py                    # CLI entrypoint
├── build_site.py              # Config-driven site builder
└── docker-compose.yml
```

## WordPress.com Setup

1. Go to [developer.wordpress.com/apps](https://developer.wordpress.com/apps/) and create an app
2. Visit the authorize URL in your browser:
   ```
   https://public-api.wordpress.com/oauth2/authorize?client_id=YOUR_ID&redirect_uri=YOUR_REDIRECT&response_type=token
   ```
3. Copy the `access_token` from the redirect URL
4. Add to `.env` as `WP_ACCESS_TOKEN`

Token expires after 14 days — re-authorize to refresh.

## Self-Hosted WordPress Setup

1. In WP Admin go to **Users → Profile → Application Passwords**
2. Create a new password and copy it
3. Add to `.env` as `WP_APP_PASSWORD`

Requires WordPress 5.6+ and HTTPS.

## Docker

```bash
docker-compose up --build
```

Runs the FastAPI backend on port 8000. Serve the frontend separately with `npm run dev` or build it with `npm run build` and serve the `dist/` folder.

## Tests

```bash
python -m pytest tests/ -v
```

11 tests covering SEO validation rules and internal link graph logic.
