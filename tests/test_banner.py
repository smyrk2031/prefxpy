from __future__ import annotations

from prefxpy.banner import (
    DEFAULT_TARGET,
    display_host,
    format_startup_banner,
    public_url,
)


def test_public_url():
    assert public_url("127.0.0.1", 9000, "/myapp/") == "http://127.0.0.1:9000/myapp/"


def test_display_host_all_interfaces():
    assert display_host("0.0.0.0") == "127.0.0.1"
    assert display_host("127.0.0.1") == "127.0.0.1"


def test_startup_banner_contains_public_url():
    text = format_startup_banner(
        public="http://127.0.0.1:9000/myapp/",
        target=DEFAULT_TARGET,
        prefix="/myapp/",
    )
    assert "Open in browser:" in text
    assert "http://127.0.0.1:9000/myapp/" in text
    assert DEFAULT_TARGET in text
