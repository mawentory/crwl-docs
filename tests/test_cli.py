"""Tests for crawler4ai.cli module."""

from crawler4ai.cli import normalize_url


class TestNormalizeUrl:
    def test_url_without_scheme_adds_https(self):
        assert normalize_url("nicegui.io") == "https://nicegui.io"

    def test_url_with_http_stays_same(self):
        assert normalize_url("http://nicegui.io") == "http://nicegui.io"

    def test_url_with_https_stays_same(self):
        assert normalize_url("https://nicegui.io") == "https://nicegui.io"

    def test_url_with_path(self):
        assert normalize_url("nicegui.io/docs") == "https://nicegui.io/docs"
