#!/usr/bin/env python3
"""
Config-driven site builder.
Usage: python build_site.py configs/example.yaml
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def apply_config_to_env(config: dict):
    wp = config.get("wordpress", {})
    if wp.get("url"):
        os.environ["WP_URL"] = wp["url"]
    if wp.get("username"):
        os.environ["WP_USERNAME"] = wp["username"]
    if wp.get("app_password"):
        os.environ["WP_APP_PASSWORD"] = wp["app_password"]
    if config.get("ai", {}).get("provider"):
        os.environ["AI_PROVIDER"] = config["ai"]["provider"]


async def run_from_config(config: dict, csv_path: str, dry_run: bool):
    from generators.async_generator import generate_pages_async
    from media.pexels import fetch_image
    from seo.linking import InternalLinkGraph
    from seo.validator import validate_page
    from wordpress.client import WordPressClient
    from wordpress.media import upload_image
    from wordpress.pages import create_page, get_or_create_category

    import pandas as pd

    site = config.get("site", {})
    domain = site.get("domain", "")
    provider = config.get("ai", {}).get("provider")
    status = config.get("publishing", {}).get("status", "publish")

    df = pd.read_csv(csv_path).fillna("")
    rows = df.to_dict(orient="records")

    console.print(f"[bold green]Building site: {domain} — {len(rows)} pages[/bold green]")

    results = await generate_pages_async(rows, domain, provider)

    # Validate all
    fail_count = 0
    for r in results:
        content = r.get("content", {})
        vr = validate_page(content, r["row"].get("keyword", ""))
        if not vr.passed:
            fail_count += 1
            console.print(f"[red]FAIL {content.get('slug', '?')}: {vr.errors}[/red]")

    console.print(f"Validation: {len(results) - fail_count}/{len(results)} passed")

    # Internal links
    graph = InternalLinkGraph()
    for r in results:
        row, content = r["row"], r.get("content", {})
        if content:
            graph.add_page(content.get("slug", ""), row.get("service", ""), row.get("city", ""), row.get("keyword", ""))
    graph.build_links()

    if dry_run:
        console.print("[yellow]Dry run complete — no WordPress upload[/yellow]")
        return

    client = WordPressClient()
    if not client.test_connection():
        console.print("[red]WordPress connection failed[/red]")
        sys.exit(1)

    parent_id = None
    if config.get("publishing", {}).get("create_parent_page"):
        parent_title = config["publishing"].get("parent_page_title", "Services")
        parent = client.post("pages", {"title": parent_title, "status": status, "slug": parent_title.lower().replace(" ", "-")})
        parent_id = parent.get("id")

    for r in results:
        row, content = r["row"], r.get("content", {})
        if not content:
            continue

        slug = content.get("slug", "")
        img_path = fetch_image(content.get("image_search_query", row.get("service", "")), row.get("service", ""), row.get("city", ""))
        media_id = upload_image(client, img_path, content.get("image_alt_text", "")) if img_path else None

        content["internal_link_suggestions"] = graph.get_links_for(slug)

        page = create_page(client, content, media_id, domain, parent_id=parent_id, status=status)
        console.print(f"[green]Published:[/green] {page.get('link', slug)}")

    console.print(f"[bold green]Site build complete: {domain}[/bold green]")


def main():
    parser = argparse.ArgumentParser(description="Config-driven site builder")
    parser.add_argument("config", help="Path to YAML config file")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config(args.config)
    apply_config_to_env(config)

    csv_path = config.get("csv_file")
    if not csv_path:
        console.print("[red]No csv_file specified in config[/red]")
        sys.exit(1)

    asyncio.run(run_from_config(config, csv_path, args.dry_run))


if __name__ == "__main__":
    main()
