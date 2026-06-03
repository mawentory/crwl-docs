"""Core crawling functionality for crawler4ai."""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
from urllib.parse import urlparse

import tldextract
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CrawlResult, DefaultMarkdownGenerator, PruningContentFilter
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy


def get_domain_parts(url: str) -> tuple[str, str | None]:
    """
    Parse domain using tldextract for accurate TLD handling.
    
    Returns (domain, subdomain) where subdomain is joined with dots if multiple.
    
    Examples:
        docs.crawl4ai.com -> ("crawl4ai", "docs")
        www.example.co.uk -> ("example", "www")
        nicegui.io -> ("nicegui", None)
        api.project.example.com -> ("example", "api.project")
    """
    # Strip protocol if present for cleaner parsing
    clean_url = re.sub(r'^https?://', '', url)
    extracted = tldextract.extract(clean_url)
    
    # tldextract returns:
    # - subdomain: "docs" for docs.crawl4ai.com
    # - domain: "crawl4ai"
    # - suffix: "com"
    
    if extracted.subdomain:
        return extracted.domain, extracted.subdomain
    return extracted.domain, None


def get_output_subpath(url: str) -> Path:
    """
    Get the relative path under the output base for a given URL.
    
    Structure:
    - Subdomain becomes subfolder: docs.crawl4ai.com -> crawl4ai/docs/
    - No subdomain: nicegui.io -> nicegui/
    """
    domain, subdomain = get_domain_parts(url)
    
    if subdomain:
        return Path(domain) / subdomain
    return Path(domain)


def sanitize_filename(name: str) -> str:
    """Sanitize string for use in filename."""
    return re.sub(r"[^\w\-_.]", "_", name)[:100]


async def crawl_to_markdown_streaming(
    url: str,
    depth: int = 5,
    output_base: Path | str | None = None,
    max_pages: int = 200,
    verbose: bool = False,
) -> AsyncGenerator[CrawlResult, None]:
    """
    Async generator that crawls a website and yields results as they complete.

    Args:
        url: Starting URL to crawl
        depth: Maximum crawl depth
        output_base: Base directory for output (default: crawled_docs)
        max_pages: Maximum number of pages to crawl
        verbose: Print crawl4ai verbose output during URL discovery

    Yields:
        CrawlResult objects for each successfully crawled page
    """
    output_base = Path(output_base) if output_base else Path("crawled_docs")
    output_subpath = get_output_subpath(url)
    output_dir = output_base / output_subpath
    output_dir.mkdir(parents=True, exist_ok=True)

    config = CrawlerRunConfig(
        verbose=verbose,
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
            max_depth=depth,
            include_external=False,
            max_pages=max_pages,
        ),
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(url=url, config=config)

        for result in results:
            if not result.success:
                continue

            md_obj = result.markdown
            markdown = md_obj.fit_markdown if md_obj and md_obj.fit_markdown else (md_obj.raw_markdown if md_obj else "")

            parsed = urlparse(result.url)
            path_slug = sanitize_filename(parsed.path.strip("/").replace("/", "_")) or "index"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"{timestamp}_{path_slug}.md"

            header = f"""---
url: {result.url}
crawled_at: {datetime.now().isoformat()}
depth: {result.metadata.get("depth", 0)}
---

"""
            output_file.write_text(header + markdown)
            result.output_file = output_file

            yield result


async def crawl_to_markdown(
    url: str,
    depth: int = 3,
    output_base: Path | str | None = None,
    max_pages: int = 50,
    verbose: bool = True,
) -> list[Path]:
    """
    Crawl a website and save pages as markdown files.

    Args:
        url: Starting URL to crawl
        depth: Maximum crawl depth
        output_base: Base directory for output (default: crawled_docs)
        max_pages: Maximum number of pages to crawl
        verbose: Print progress messages

    Returns:
        List of paths to created markdown files
    """
    output_files = []
    async for result in crawl_to_markdown_streaming(url, depth, output_base, max_pages):
        output_files.append(result.output_file)
        if verbose:
            print(f"  [{len(output_files)}] {result.url}")

    return output_files
