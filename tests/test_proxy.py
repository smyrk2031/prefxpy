from __future__ import annotations

import socket

import httpx
import pytest
from aiohttp import web

from prefxpy.proxy import ProxyConfig, create_app, normalize_prefix


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


async def _start_server(app: web.Application, host: str, port: int):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    return runner


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("/myapp", "/myapp/"),
        ("myapp", "/myapp/"),
        ("/", "/"),
    ],
)
def test_normalize_prefix(raw: str, expected: str) -> None:
    assert normalize_prefix(raw) == expected


@pytest.mark.asyncio
async def test_proxy_forwards_path_query_and_forwarded_headers() -> None:
    async def upstream_echo(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "path_qs": request.path_qs,
                "xfh": request.headers.get("X-Forwarded-Host"),
                "xfp": request.headers.get("X-Forwarded-Prefix"),
                "xfproto": request.headers.get("X-Forwarded-Proto"),
            }
        )

    upstream_app = web.Application()
    upstream_app.router.add_get("/{tail:.*}", upstream_echo)
    upstream_port = _free_port()
    upstream_runner = await _start_server(upstream_app, "127.0.0.1", upstream_port)

    proxy_port = _free_port()
    proxy_app = create_app(
        ProxyConfig(target=f"http://127.0.0.1:{upstream_port}", prefix="/myapp/")
    )
    proxy_runner = await _start_server(proxy_app, "127.0.0.1", proxy_port)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"http://127.0.0.1:{proxy_port}/myapp/hello/world?x=1")
            res.raise_for_status()
            payload = res.json()
        assert payload["path_qs"] == "/hello/world?x=1"
        assert payload["xfp"] == "/myapp"
        assert payload["xfproto"] == "http"
    finally:
        await proxy_runner.cleanup()
        await upstream_runner.cleanup()


@pytest.mark.asyncio
async def test_root_shows_help_html() -> None:
    async def upstream_ok(_: web.Request) -> web.Response:
        return web.Response(text="ok")

    upstream_app = web.Application()
    upstream_app.router.add_get("/{tail:.*}", upstream_ok)
    upstream_port = _free_port()
    upstream_runner = await _start_server(upstream_app, "127.0.0.1", upstream_port)

    proxy_port = _free_port()
    proxy_app = create_app(
        ProxyConfig(target=f"http://127.0.0.1:{upstream_port}", prefix="/myapp/")
    )
    proxy_runner = await _start_server(proxy_app, "127.0.0.1", proxy_port)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"http://127.0.0.1:{proxy_port}/")
            res.raise_for_status()
        assert "PrefxPy" in res.text
        assert f"http://127.0.0.1:{proxy_port}/myapp/" in res.text
    finally:
        await proxy_runner.cleanup()
        await upstream_runner.cleanup()


@pytest.mark.asyncio
async def test_non_prefix_path_shows_friendly_404() -> None:
    async def upstream_ok(_: web.Request) -> web.Response:
        return web.Response(text="ok")

    upstream_app = web.Application()
    upstream_app.router.add_get("/{tail:.*}", upstream_ok)
    upstream_port = _free_port()
    upstream_runner = await _start_server(upstream_app, "127.0.0.1", upstream_port)

    proxy_port = _free_port()
    proxy_app = create_app(
        ProxyConfig(target=f"http://127.0.0.1:{upstream_port}", prefix="/myapp/")
    )
    proxy_runner = await _start_server(proxy_app, "127.0.0.1", proxy_port)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"http://127.0.0.1:{proxy_port}/hello")
        assert res.status_code == 404
        assert "/myapp/" in res.text
    finally:
        await proxy_runner.cleanup()
        await upstream_runner.cleanup()

@pytest.mark.asyncio
async def test_proxy_rewrites_location_header() -> None:
    async def upstream_redirect(_: web.Request) -> web.Response:
        raise web.HTTPFound(location="/login")

    upstream_app = web.Application()
    upstream_app.router.add_get("/{tail:.*}", upstream_redirect)
    upstream_port = _free_port()
    upstream_runner = await _start_server(upstream_app, "127.0.0.1", upstream_port)

    proxy_port = _free_port()
    proxy_app = create_app(
        ProxyConfig(target=f"http://127.0.0.1:{upstream_port}", prefix="/myapp/")
    )
    proxy_runner = await _start_server(proxy_app, "127.0.0.1", proxy_port)

    try:
        async with httpx.AsyncClient(follow_redirects=False) as client:
            res = await client.get(f"http://127.0.0.1:{proxy_port}/myapp/start")
        assert res.status_code == 302
        assert res.headers["location"] == "/myapp/login"
    finally:
        await proxy_runner.cleanup()
        await upstream_runner.cleanup()


@pytest.mark.asyncio
async def test_proxy_sends_config_extra_headers_and_forwarded_wins() -> None:
    async def upstream_echo(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "xdev": request.headers.get("X-Dev-Mode"),
                "xfp": request.headers.get("X-Forwarded-Prefix"),
            }
        )

    upstream_app = web.Application()
    upstream_app.router.add_get("/{tail:.*}", upstream_echo)
    upstream_port = _free_port()
    upstream_runner = await _start_server(upstream_app, "127.0.0.1", upstream_port)

    proxy_port = _free_port()
    extra = (("X-Dev-Mode", "1"), ("X-Forwarded-Prefix", "/wrong"))
    proxy_app = create_app(
        ProxyConfig(
            target=f"http://127.0.0.1:{upstream_port}",
            prefix="/myapp/",
            extra_headers=extra,
        )
    )
    proxy_runner = await _start_server(proxy_app, "127.0.0.1", proxy_port)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"http://127.0.0.1:{proxy_port}/myapp/hi")
            res.raise_for_status()
            payload = res.json()
        assert payload["xdev"] == "1"
        assert payload["xfp"] == "/myapp"
    finally:
        await proxy_runner.cleanup()
        await upstream_runner.cleanup()
