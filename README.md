# PrefxPy

[![CI](https://github.com/smyrk2031/prefxpy/actions/workflows/ci.yml/badge.svg)](https://github.com/smyrk2031/prefxpy/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/prefxpy)](https://pypi.org/project/prefxpy/)
[![Python](https://img.shields.io/pypi/pyversions/prefxpy)](https://pypi.org/project/prefxpy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A small local reverse proxy for reproducing **production subpath / reverse-proxy issues** during development.

Works well when your app behaves differently behind a path prefix (e.g. `/myapp/`) or with `X-Forwarded-*` headers — problems that often only show up in staging or production.

**Not** a high-performance production proxy. Use it for local verification with FastAPI, Django, Flask, and similar stacks.

## Install

```bash
pip install prefxpy
```

## Quick start

```bash
prefxpy
```

Defaults:

- Public URL: `http://127.0.0.1:9000/myapp/`
- Upstream: `http://127.0.0.1:8000`

Another upstream port:

```bash
prefxpy --target http://127.0.0.1:5000
```

On startup, PrefxPy prints the **URL to open** in your browser.

## Config file

```bash
prefxpy --config prefxpy.toml
```

See [`examples/prefxpy.example.toml`](examples/prefxpy.example.toml) for a sample. CLI flags override file values when set.

By default PrefxPy sets these forwarded headers on upstream requests:

- `X-Forwarded-Host`
- `X-Forwarded-Proto`
- `X-Forwarded-Prefix`
- `X-Forwarded-For`

## Development

```bash
git clone https://github.com/smyrk2031/prefxpy.git
cd prefxpy
pip install -e ".[dev]"
pytest
```

Publishing to TestPyPI / PyPI: [`docs/PYPI.md`](docs/PYPI.md).

## Documentation

| Language | Topic |
|----------|-------|
| 日本語 | [仕様](docs/仕様.md) · [設計](docs/設計.md) |
| English | This README · [Project site](https://smyrk2031.github.io/prefxpy/) |

## License

PrefxPy is released under the [MIT License](LICENSE).

Third-party licenses for runtime dependencies (aiohttp, httpx, etc.) are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
