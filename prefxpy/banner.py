from __future__ import annotations

DEFAULT_TARGET = "http://127.0.0.1:8000"


def display_host(bind_host: str) -> str:
    """Host name to show in URLs when bound to all interfaces."""
    if bind_host in ("0.0.0.0", "::"):
        return "127.0.0.1"
    return bind_host


def public_url(bind_host: str, bind_port: int, prefix: str) -> str:
    host = display_host(bind_host)
    return f"http://{host}:{bind_port}{prefix}"


def format_startup_banner(*, public: str, target: str, prefix: str) -> str:
    return (
        "\n"
        "[PrefxPy]\n"
        "\n"
        f"  Open in browser:  {public}\n"
        f"  Target (upstream):  {target}\n"
        f"  Prefix:             {prefix}\n"
        "\n"
        "  Notes:\n"
        "  - Start your dev server first (e.g. uvicorn main:app --port 8000).\n"
        "  - The root URL (/) shows this help; your app lives under the prefix above.\n"
        "  - Health check: /_prefx/health\n"
        "\n"
        "  Features: reverse proxy, forwarded headers, Location rewrite\n"
    )


def format_root_help_html(*, public: str, target: str, prefix: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <title>PrefxPy</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; line-height: 1.5; }}
    code {{ background: #f4f4f4; padding: 0.1em 0.35em; border-radius: 4px; }}
    a {{ font-weight: 600; }}
  </style>
</head>
<body>
  <h1>PrefxPy</h1>
  <p>本番のサブパス配下をローカルで再現する開発用プロキシです。</p>
  <p><strong>アプリはこちらを開いてください:</strong><br>
     <a href="{public}">{public}</a></p>
  <p>転送先: <code>{target}</code><br>
     Prefix: <code>{prefix}</code></p>
  <p><small>ルート <code>/</code> ではアプリは表示されません（仕様です）。</small></p>
</body>
</html>"""
