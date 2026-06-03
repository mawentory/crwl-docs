"""CLI interface for crawler4ai."""

import asyncio
import sys

import click

from crawler4ai.core import crawl_to_markdown, get_output_subpath


@click.command()
@click.argument("url")
@click.argument("depth", type=int, default=3)
@click.option(
    "--max-pages", "-n",
    type=int,
    default=50,
    help="Maximum number of pages to crawl (default: 50)",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="crawled_docs",
    help="Output directory (default: crawled_docs)",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress progress output",
)
def cli(url: str, depth: int, max_pages: int, output: str, quiet: bool) -> None:
    """
    Crawl a website and save pages as markdown documentation.

    URL     Starting URL to crawl
    DEPTH   Maximum crawl depth (default: 3)

    Examples:

        crwl-docs https://docs.example.com 2
        crwl-docs https://docs.example.com 3 --max-pages 100
        crwl-docs https://api.project.org 2 --output ./my-docs
        crwl-docs https://docs.example.com 2 -n 25 -o ./output -q
    """
    verbose = not quiet
    
    if verbose:
        click.echo(f"Starting crawl of {url}")
        click.echo(f"  Depth: {depth}, Max pages: {max_pages}")
        click.echo(f"  Output: {output}/{get_output_subpath(url)}")
        click.echo("")

    try:
        output_files = asyncio.run(
            crawl_to_markdown(
                url=url,
                depth=depth,
                output_base=output,
                max_pages=max_pages,
                verbose=verbose,
            )
        )
        
        if output_files:
            if verbose:
                click.echo(f"\nSuccessfully saved {len(output_files)} pages to:")
                click.echo(f"  {output}/{get_output_subpath(url)}/")
            else:
                for f in output_files:
                    click.echo(f)
            sys.exit(0)
        else:
            if verbose:
                click.echo("No pages were crawled.", err=True)
            sys.exit(1)
            
    except KeyboardInterrupt:
        if verbose:
            click.echo("\nCrawl interrupted by user.", err=True)
        sys.exit(130)
    except Exception as e:
        if verbose:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
