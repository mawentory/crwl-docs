# crwl-docs

CLI wrapper around [crawler4ai](https://github.com/crawl4ai/crawl4ai) for crawling documentation sites to markdown.

## Installation

Requires Python 3.13+

```bash
uv tool install git+https://github.com/mawentory/crwl-dcos
```

## Usage

```bash
crwl-docs <url> [options]

# Examples
crwl-docs https://nicegui.io/documentation
crwl-docs https://docs.python.org/3/ --depth 2
crwl-docs https://fastapi.tiangolo.com/ --max-pages 50
```

### Options

- `--depth, -d`: Crawl depth (default: 3)
- `--max-pages, -m`: Maximum pages to crawl (default: 100)
- `--output, -o`: Output directory (default: crawled_docs/)
