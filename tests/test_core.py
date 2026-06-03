"""Tests for crawler4ai.core module."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from crawler4ai.core import (
    crawl_to_markdown,
    crawl_to_markdown_streaming,
    get_domain_parts,
    get_output_subpath,
    sanitize_filename,
)


class TestGetDomainParts:
    def test_simple_domain(self):
        assert get_domain_parts("nicegui.io") == ("nicegui", None)

    def test_subdomain(self):
        assert get_domain_parts("docs.crawl4ai.com") == ("crawl4ai", "docs")

    def test_www_preserved_as_subdomain(self):
        assert get_domain_parts("www.example.com") == ("example", "www")

    def test_compound_suffix_co_uk(self):
        assert get_domain_parts("bbc.co.uk") == ("bbc", None)

    def test_multi_level_subdomain(self):
        assert get_domain_parts("api.v2.github.com") == ("github", "api.v2")

    def test_with_url_scheme(self):
        assert get_domain_parts("https://docs.python.org/3/") == ("python", "docs")

    def test_documentation_co_uk(self):
        assert get_domain_parts("documentation.co.uk") == ("documentation", None)

    def test_www_bbc_co_uk(self):
        assert get_domain_parts("www.bbc.co.uk") == ("bbc", "www")


class TestGetOutputSubpath:
    def test_no_subdomain(self):
        assert get_output_subpath("nicegui.io") == Path("nicegui")

    def test_with_subdomain(self):
        assert get_output_subpath("docs.crawl4ai.com") == Path("crawl4ai/docs")

    def test_compound_suffix(self):
        assert get_output_subpath("documentation.co.uk") == Path("documentation")

    def test_www_subdomain(self):
        assert get_output_subpath("www.example.org/docs") == Path("example/www")

    def test_multi_level_subdomain(self):
        assert get_output_subpath("api.v2.github.com") == Path("github/api.v2")


class TestSanitizeFilename:
    def test_normal_string(self):
        assert sanitize_filename("hello_world") == "hello_world"

    def test_special_characters(self):
        assert sanitize_filename("file@#$.txt") == "file___.txt"

    def test_long_filename_truncated(self):
        long_name = "a" * 200
        assert len(sanitize_filename(long_name)) == 100


class TestAsyncCrawl:
    def test_crawl_to_markdown_streaming_is_async_generator(self):
        """Test that crawl_to_markdown_streaming is an async generator."""
        import inspect
        assert inspect.isasyncgenfunction(crawl_to_markdown_streaming)

    def test_crawl_to_markdown_is_coroutine_function(self):
        """Test that crawl_to_markdown is an async function."""
        import inspect
        assert inspect.iscoroutinefunction(crawl_to_markdown)
