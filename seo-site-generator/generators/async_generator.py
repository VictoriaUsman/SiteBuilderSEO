import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

load_dotenv()

MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_PAGES", "10"))


async def _generate_one(row: dict, domain: str, provider: Optional[str], semaphore: asyncio.Semaphore,
                        gemini_key: str = None, openai_key: str = None) -> dict:
    async with semaphore:
        loop = asyncio.get_event_loop()
        from generators.content_generator import generate_page
        import functools
        fn = functools.partial(generate_page, row["keyword"], row["city"], row["service"], domain,
                               provider, gemini_key, openai_key)
        result = await loop.run_in_executor(None, fn)
        return {"row": row, "content": result, "error": None}


async def generate_pages_async(rows: list[dict], domain: str, provider: Optional[str] = None,
                                gemini_key: str = None, openai_key: str = None) -> list[dict]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
    ) as progress:
        task = progress.add_task("Generating pages...", total=len(rows))

        async def track(row):
            result = await _generate_one(row, domain, provider, semaphore, gemini_key, openai_key)
            progress.advance(task)
            return result

        tasks = [track(row) for row in rows]
        results = await asyncio.gather(*tasks, return_exceptions=False)

    return results
