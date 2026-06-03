"""CLI interface for crawler4ai."""

import asyncio
import re
import sys

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TaskProgressColumn, TextColumn

from crawler4ai.core import crawl_to_markdown_streaming, get_output_subpath

console = Console()


def normalize_url(url: str) -> str:
    """Add https:// prefix if URL doesn't have a scheme."""
    if not re.match(r'^https?://', url, re.IGNORECASE):
        return f"https://{url}"
    return url


async def run_crawl(url: str, depth: int, max_pages: int, output_base: str, verbose: bool) -> list:
    """Run the crawl with a rich progress bar."""
    output_files = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=False,
    ) as progress:
        task = progress.add_task("Crawling...", total=max_pages)

        async for result in crawl_to_markdown_streaming(
            url=url,
            depth=depth,
            output_base=output_base,
            max_pages=max_pages,
            verbose=False,
        ):
            output_files.append(result.output_file)
            progress.update(
                task,
                advance=1,
                description=f"[cyan]{len(output_files)}/{max_pages}[/cyan] {result.url[:60]}",
            )
            click.echo(result.url)

    return output_files


async def run_crawl_verbose(url: str, depth: int, max_pages: int, output_base: str) -> list:
    """
    Verbose crawl mode: Let crawl4ai output freely during URL discovery,
    then show a final summary.
    """
    output_files = []

    async for result in crawl_to_markdown_streaming(
        url=url,
        depth=depth,
        output_base=output_base,
        max_pages=max_pages,
        verbose=True,
    ):
        output_files.append(result.output_file)

    return output_files


@click.command()
@click.argument("url")
@click.argument("depth", type=int, default=3)
@click.option(
    "--max-pages", "-n",
    type=int,
    default=100,
    help="Maximum number of pages to crawl (default: 100)",
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
    MAX_PAGES Maximum number of pages to crawl (default: 100)

    Examples:

        crwl-docs https://docs.example.com 2
        crwl-docs https://docs.example.com 3 --max-pages 100
        crwl-docs https://api.project.org 2 --output ./my-docs
        crwl-docs https://docs.example.com 2 -n 25 -o ./output -q
    """
    verbose = not quiet

    try:
        url = normalize_url(url)

        if verbose:
            click.echo(f"Starting crawl of {url}")
            click.echo(f"  Depth: {depth}, Max pages: {max_pages}")
            click.echo(f"  Output: {output}/{get_output_subpath(url)}")
            click.echo("")

        output_files = asyncio.run(
            run_crawl_verbose(
                url=url,
                depth=depth,
                max_pages=max_pages,
                output_base=output,
            )
        ) if verbose else asyncio.run(
            run_crawl(
                url=url,
                depth=depth,
                max_pages=max_pages,
                output_base=output,
                verbose=verbose,
            )
        )

        if output_files:
            if verbose:
                click.echo(f"\n[green]Successfully[/green] saved [bold]{len(output_files)}[/bold] pages to:")
                click.echo(f"  [cyan]{output}/{get_output_subpath(url)}/[/cyan]")
            else:
                for f in output_files:
                    click.echo(f)
            sys.exit(0)
        else:
            if verbose:
                click.echo("[yellow]No pages were crawled.[/yellow]", err=True)
            sys.exit(1)

    except KeyboardInterrupt:
        if verbose:
            click.echo("\n[yellow]Crawl interrupted by user.[/yellow]", err=True)
        sys.exit(130)
    except Exception as e:
        if verbose:
            click.echo(f"[red]Error:[/red] {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
