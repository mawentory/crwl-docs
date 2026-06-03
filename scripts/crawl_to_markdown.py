import asyncio
import re
import sys
from pathlib import Path
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, DefaultMarkdownGenerator, PruningContentFilter
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy


def extract_domain_name(url: str) -> str:
    """Extract short name from URL domain."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    domain = re.sub(r'^www\.', '', domain)
    parts = domain.split('.')
    return parts[0] if parts else domain


def sanitize_filename(name: str) -> str:
    """Sanitize string for use in filename."""
    return re.sub(r'[^\w\-_.]', '_', name)[:100]


async def crawl_to_markdown(url: str, output_base: Path = None, max_pages: int = 50) -> list[Path]:
    output_base = output_base or Path(".cache/docs")
    short_name = extract_domain_name(url)
    output_dir = output_base / short_name
    output_dir.mkdir(parents=True, exist_ok=True)

    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(),
            options={
                "ignore_links": True,
                "ignore_images": True,
                "escape_html": False,
                "body_width": 0,
                "skip_internal_links": True,
            }
        ),
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=3,
            include_external=False,
            max_pages=max_pages,
        ),
        verbose=True
    )

    output_files = []
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(url=url, config=config)

        for i, result in enumerate(results):
            if not result.success:
                continue

            md_obj = result.markdown
            markdown = md_obj.fit_markdown if md_obj and md_obj.fit_markdown else (md_obj.raw_markdown if md_obj else "")

            from urllib.parse import urlparse
            parsed = urlparse(result.url)
            path_slug = sanitize_filename(parsed.path.strip("/").replace("/", "_")) or "index"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"{timestamp}_{i:03d}_{path_slug}.md"

            header = f"""---
url: {result.url}
crawled_at: {datetime.now().isoformat()}
depth: {result.metadata.get("depth", 0)}
---

"""
            output_file.write_text(header + markdown)
            output_files.append(output_file)

    return output_files


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/crawl_to_markdown.py <url> [max_pages]")
        sys.exit(1)

    url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    output_files = asyncio.run(crawl_to_markdown(url, max_pages=max_pages))
    print(f"Saved {len(output_files)} pages to: .cache/docs/{extract_domain_name(url)}/")
