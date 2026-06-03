"""Legacy script - use 'crwl-docs' CLI instead."""

import asyncio
import sys
from pathlib import Path

from crawler4ai import crawl_to_markdown


def extract_domain_name(url: str) -> str:
    """Extract short name from URL domain."""
    from urllib.parse import urlparse
    import re
    domain = urlparse(url).netloc
    domain = re.sub(r'^www\.', '', domain)
    parts = domain.split('.')
    return parts[0] if parts else domain


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/crawl_to_markdown.py <url> [max_pages]")
        print("This script is depricated!")
        print("Consider using: crwl-docs <url> <depth>")
        sys.exit(1)

    url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    output_files = asyncio.run(crawl_to_markdown(url, max_pages=max_pages))
    print(f"Saved {len(output_files)} pages to: crawled_docs/{extract_domain_name(url)}/")
