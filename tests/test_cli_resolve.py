from __future__ import annotations

import textwrap

import pytest

from prefxpy.cli import build_parser, resolve_settings
from prefxpy.config import load_prefx_toml


def test_resolve_from_file_only(tmp_path):
    p = tmp_path / "prefxpy.toml"
    p.write_text(
        textwrap.dedent(
            """\
            target = "http://127.0.0.1:4000"
            prefix = "/demo/"
            host = "0.0.0.0"
            port = 8081
            log_level = "warning"
            [headers]
            X-Dev-Mode = "1"
            """
        ),
        encoding="utf-8",
    )
    args = build_parser().parse_args(["--config", str(p)])
    settings = resolve_settings(args, load_prefx_toml(p))
    assert settings.target == "http://127.0.0.1:4000"
    assert settings.prefix == "/demo/"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8081
    assert settings.log_level == "WARNING"
    assert ("X-Dev-Mode", "1") in settings.extra_headers


def test_cli_overrides_file(tmp_path):
    p = tmp_path / "prefxpy.toml"
    p.write_text(
        'target = "http://old:1"\nprefix = "/old/"\nport = 1111\n',
        encoding="utf-8",
    )
    args = build_parser().parse_args(
        ["--config", str(p), "--target", "http://new:2", "--prefix", "/new/", "--port", "2222"]
    )
    settings = resolve_settings(args, load_prefx_toml(p))
    assert settings.target == "http://new:2"
    assert settings.prefix == "/new/"
    assert settings.port == 2222


def test_default_target_without_args_or_config():
    args = build_parser().parse_args([])
    settings = resolve_settings(args, {})
    assert settings.target == "http://127.0.0.1:8000"
    assert settings.prefix == "/myapp/"
    assert settings.port == 9000
