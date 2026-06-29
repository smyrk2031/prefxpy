from __future__ import annotations

import textwrap

import pytest

from prefxpy.config import load_prefx_toml, normalize_headers


def test_load_prefx_toml(tmp_path):
    p = tmp_path / "prefxpy.toml"
    p.write_text(
        textwrap.dedent(
            """\
            target = "http://127.0.0.1:8000"
            prefix = "/demo/"
            port = 9090
            [headers]
            X-Dev = "1"
            """
        ),
        encoding="utf-8",
    )
    data = load_prefx_toml(p)
    assert data["target"] == "http://127.0.0.1:8000"
    assert data["prefix"] == "/demo/"
    assert data["port"] == 9090
    assert data["headers"]["X-Dev"] == "1"


def test_normalize_headers_valid():
    hdrs = normalize_headers({"A": "b", "C": 3})
    assert ("A", "b") in hdrs
    assert ("C", "3") in hdrs
    assert len(hdrs) == 2


def test_normalize_headers_invalid():
    with pytest.raises(ValueError, match="table"):
        normalize_headers("oops")


def test_load_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_prefx_toml(tmp_path / "nope.toml")
