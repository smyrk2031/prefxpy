from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import httpx
from aiohttp import web

from prefxpy.banner import format_root_help_html

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def normalize_prefix(prefix: str) -> str:
    clean = (prefix or "/").strip()
    if not clean.startswith("/"):
        clean = f"/{clean}"
    if not clean.endswith("/"):
        clean = f"{clean}/"
    return clean


def _join_target_url(target_base: str, stripped_path_qs: str) -> str:
    base = target_base.rstrip("/")
    if stripped_path_qs.startswith("/"):
        return f"{base}{stripped_path_qs}"
    return f"{base}/{stripped_path_qs}"


def _rewrite_location(location: str, prefix: str) -> str:
    if location.startswith("/"):
        return f"{prefix.rstrip('/')}{location}"
    return location


@dataclass(frozen=True)
class ProxyConfig:
    target: str
    prefix: str = "/myapp/"
    extra_headers: tuple[tuple[str, str], ...] = ()

    def normalized_prefix(self) -> str:
        return normalize_prefix(self.prefix)


CONFIG_KEY = web.AppKey("config", ProxyConfig)
CLIENT_KEY = web.AppKey("client", httpx.AsyncClient)


def _filter_headers(headers: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {k: v for k, v in headers if k.lower() not in HOP_BY_HOP_HEADERS}


def _build_forwarded_headers(request: web.Request, prefix: str) -> dict[str, str]:
    client_ip = request.remote or "127.0.0.1"
    return {
        "X-Forwarded-Host": request.host,
        "X-Forwarded-Proto": request.scheme,
        "X-Forwarded-Prefix": prefix.rstrip("/"),
        "X-Forwarded-For": client_ip,
    }


async def _root_help(request: web.Request) -> web.Response:
    config: ProxyConfig = request.app[CONFIG_KEY]
    prefix = config.normalized_prefix()
    public = f"http://{request.host}{prefix}"
    html = format_root_help_html(public=public, target=config.target, prefix=prefix)
    return web.Response(text=html, content_type="text/html", charset="utf-8")


async def _prefix_required_help(request: web.Request) -> web.Response:
    config: ProxyConfig = request.app[CONFIG_KEY]
    prefix = config.normalized_prefix()
    public = f"http://{request.host}{prefix}"
    text = (
        f"PrefxPy: open your app at {public}\n"
        f"(paths must start with prefix '{prefix}')\n"
    )
    return web.Response(text=text, status=404, content_type="text/plain", charset="utf-8")


async def _proxy_handler(request: web.Request) -> web.StreamResponse:
    config: ProxyConfig = request.app[CONFIG_KEY]
    client: httpx.AsyncClient = request.app[CLIENT_KEY]
    prefix = config.normalized_prefix()

    incoming_path_qs = request.path_qs
    if not incoming_path_qs.startswith(prefix):
        return await _prefix_required_help(request)

    stripped_path_qs = incoming_path_qs[len(prefix) - 1 :]
    upstream_url = _join_target_url(config.target, stripped_path_qs)

    base_headers = _filter_headers(request.headers.items())
    forwarded = _build_forwarded_headers(request, prefix)
    for name, value in config.extra_headers:
        base_headers[name] = value
    base_headers.update(forwarded)
    base_headers.pop("Host", None)

    body = await request.read()

    upstream = await client.request(
        request.method,
        upstream_url,
        headers=base_headers,
        content=body,
        follow_redirects=False,
    )

    response_headers = _filter_headers(upstream.headers.items())
    for key, value in list(response_headers.items()):
        if key.lower() == "location":
            response_headers[key] = _rewrite_location(value, prefix)

    return web.Response(
        status=upstream.status_code,
        body=upstream.content,
        headers=response_headers,
    )


async def _health(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def create_app(config: ProxyConfig) -> web.Application:
    app = web.Application()
    app[CONFIG_KEY] = config

    async def on_startup(_: web.Application) -> None:
        app[CLIENT_KEY] = httpx.AsyncClient(timeout=20)

    async def on_cleanup(_: web.Application) -> None:
        await app[CLIENT_KEY].aclose()

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    app.router.add_get("/", _root_help)
    app.router.add_get("/_prefx/health", _health)
    app.router.add_route("*", "/{path:.*}", _proxy_handler)
    return app

