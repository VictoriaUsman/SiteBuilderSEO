#!/usr/bin/env python3
"""
AI Local SEO Site Builder
Usage: python main.py --csv configs/sample_keywords.csv --domain example.com
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from generators.async_generator import generate_pages_async
from media.pexels import fetch_image
from seo.linking import InternalLinkGraph
from seo.validator import validate_batch, validate_page
from wordpress.client import WordPressClient
from wordpress.media import upload_image
from wordpress.pages import create_page

load_dotenv()
console = Console()


def load_csv(path: str) -> list[dict]:
    df = pd.read_csv(path)
    required = {"keyword", "city", "service"}
    if not required.issubset(df.columns):
        console.print(f"[red]CSV must have columns: {required}[/red]")
        sys.exit(1)
    return df.fillna("").to_dict(orient="records")


def save_output(results: list[dict], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    for r in results:
        if r.get("content"):
            slug = r["content"].get("slug", "page")
            with open(output_dir / f"{slug}.json", "w") as f:
                json.dump(r["content"], f, indent=2)


def print_validation_report(results: list[dict]):
    table = Table(title="SEO Validation Report", show_lines=True)
    table.add_column("Slug", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Errors", style="red")
    table.add_column("Warnings", style="yellow")

    for r in results:
        content = r.get("content", {})
        row_data = r.get("row", {})
        keyword = row_data.get("keyword", "")
        vr = validate_page(content, keyword)
        status = "[green]PASS[/green]" if vr.passed else "[red]FAIL[/red]"
        table.add_row(
            content.get("slug", "?"),
            status,
            "\n".join(vr.errors) or "-",
            "\n".join(vr.warnings) or "-",
        )

    console.print(table)

    batch = validate_batch(results)
    if batch["duplicate_slugs"]:
        console.print(f"[red]Duplicate slugs: {batch['duplicate_slugs']}[/red]")
    if batch["duplicate_titles"]:
        console.print(f"[yellow]Duplicate titles: {batch['duplicate_titles']}[/yellow]")


async def run(args):
    rows = load_csv(args.csv)
    domain = args.domain
    console.print(f"[bold green]Loaded {len(rows)} rows from {args.csv}[/bold green]")

    # Step 1: Generate content
    console.rule("[bold blue]Step 1: Generating Content[/bold blue]")
    results = await generate_pages_async(rows, domain, args.provider)
    save_output(results, Path("output/pages"))
    console.print(f"[green]Generated {len(results)} pages[/green]")

    # Step 2: Validate
    console.rule("[bold blue]Step 2: SEO Validation[/bold blue]")
    print_validation_report(results)

    # Step 3: Build internal link graph
    console.rule("[bold blue]Step 3: Internal Linking Graph[/bold blue]")
    graph = InternalLinkGraph()
    for r in results:
        row, content = r["row"], r.get("content", {})
        if content:
            graph.add_page(content.get("slug", ""), row["service"], row["city"], row["keyword"])
    graph.build_links()
    summary = graph.summary()
    console.print(f"Pages: {summary['total_pages']} | Links built: {summary['total_links']}")
    console.print(f"Hub pages: {summary['hub_pages']}")

    if args.dry_run:
        console.print("\n[yellow]--dry-run set: skipping WordPress upload[/yellow]")
        return

    # Step 4: Upload to WordPress
    console.rule("[bold blue]Step 4: Uploading to WordPress[/bold blue]")
    client = WordPressClient()
    if not client.test_connection():
        console.print("[red]WordPress connection failed. Check WP_URL, WP_USERNAME, WP_APP_PASSWORD in .env[/red]")
        sys.exit(1)

    for r in results:
        row, content = r["row"], r.get("content", {})
        if not content:
            continue

        slug = content.get("slug", "")
        console.print(f"  Uploading: [cyan]{slug}[/cyan]")

        # Fetch and upload image
        media_id = None
        if not args.no_images:
            img_path = fetch_image(
                content.get("image_search_query", row["service"]),
                row["service"],
                row["city"],
            )
            media_id = upload_image(client, img_path, content.get("image_alt_text", ""))

        # Inject graph-computed internal links
        graph_links = graph.get_links_for(slug)
        if graph_links:
            content["internal_link_suggestions"] = graph_links

        page = create_page(client, content, media_id, domain, status=args.status)
        console.print(f"    [green]Published: {page.get('link', slug)}[/green]")

    console.rule("[bold green]Done[/bold green]")


def main():
    parser = argparse.ArgumentParser(description="AI Local SEO Site Builder")
    parser.add_argument("--csv", required=True, help="Path to keyword CSV file")
    parser.add_argument("--domain", required=True, help="Target domain (e.g. example.com)")
    parser.add_argument("--provider", choices=["gemini", "openai"], help="AI provider override")
    parser.add_argument("--status", default="publish", choices=["publish", "draft"], help="WP page status")
    parser.add_argument("--dry-run", action="store_true", help="Generate content but skip WordPress upload")
    parser.add_argument("--no-images", action="store_true", help="Skip image download/upload")
    args = parser.parse_args()

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
