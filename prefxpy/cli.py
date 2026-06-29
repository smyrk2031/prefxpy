from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass

from aiohttp import web

from prefxpy.banner import DEFAULT_TARGET, format_startup_banner, public_url
from prefxpy.config import load_prefx_toml, normalize_headers
from prefxpy.proxy import ProxyConfig, create_app, normalize_prefix

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


@dataclass(frozen=True)
class RunSettings:
    target: str
    prefix: str
    host: str
    port: int
    log_level: str
    extra_headers: tuple[tuple[str, str], ...]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prefxpy",
        description="Simulate production prefix/reverse-proxy behavior in local development.",
    )
    parser.add_argument(
        "--config",
        default=None,
        metavar="PATH",
        help="TOML config (prefxpy.toml). CLI options override file values when set.",
    )
    parser.add_argument(
        "--target",
        default=None,
        help=f"Upstream app URL (overrides config). Default: {DEFAULT_TARGET}",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Public path prefix (overrides config). Default: /myapp/",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Bind host (overrides config). Default: 127.0.0.1",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Bind port (overrides config). Default: 9000",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        choices=list(LOG_LEVELS),
        help=f"Log level (overrides config). Default: INFO. Choices: {', '.join(LOG_LEVELS)}",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def resolve_settings(args: argparse.Namespace, file_cfg: dict) -> RunSettings:
    if args.target is not None:
        target = args.target
    else:
        target = file_cfg.get("target", DEFAULT_TARGET)

    if not isinstance(target, str) or not target.strip():
        raise ValueError("target must be a non-empty URL string")

    prefix_raw = args.prefix if args.prefix is not None else file_cfg.get("prefix", "/myapp/")
    if not isinstance(prefix_raw, str):
        raise ValueError("prefix must be a string")

    host = args.host if args.host is not None else file_cfg.get("host", "127.0.0.1")
    if not isinstance(host, str):
        raise ValueError("host must be a string")

    if args.port is not None:
        port = args.port
    else:
        port = _coerce_port(file_cfg.get("port", 9000))

    if args.log_level is not None:
        log_level = args.log_level
    else:
        raw_ll = file_cfg.get("log_level", "INFO")
        if not isinstance(raw_ll, str):
            raise ValueError("log_level must be a string")
        log_level = raw_ll.upper()

    if log_level not in LOG_LEVELS:
        raise ValueError(f"log_level must be one of: {', '.join(LOG_LEVELS)}")

    extra = normalize_headers(file_cfg.get("headers"))

    return RunSettings(
        target=target.strip(),
        prefix=prefix_raw.strip(),
        host=host.strip(),
        port=port,
        log_level=log_level,
        extra_headers=extra,
    )


def _coerce_port(raw: object) -> int:
    if isinstance(raw, bool):
        raise ValueError("port must be an integer")
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str):
        return int(raw.strip(), 10)
    raise ValueError("port must be an integer")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    file_cfg: dict = {}
    if args.config:
        file_cfg = load_prefx_toml(args.config)

    try:
        settings = resolve_settings(args, file_cfg)
    except ValueError as exc:
        print(f"prefxpy: error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    logging.basicConfig(level=getattr(logging, settings.log_level))

    prefix = normalize_prefix(settings.prefix)
    public = public_url(settings.host, settings.port, prefix)
    print(
        format_startup_banner(
            public=public,
            target=settings.target,
            prefix=prefix,
        )
    )

    config = ProxyConfig(
        target=settings.target,
        prefix=settings.prefix,
        extra_headers=settings.extra_headers,
    )
    app = create_app(config)
    web.run_app(app, host=settings.host, port=settings.port, print=None)


if __name__ == "__main__":
    main()
