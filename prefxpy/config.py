from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load_prefx_toml(path: str | Path) -> dict[str, Any]:
    """Load a prefxpy TOML file and return the top-level table as a dict."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Config file not found: {p}")
    with p.open("rb") as f:
        data = tomllib.load(f)
    if not isinstance(data, dict):
        raise ValueError("Invalid TOML root: expected a table")
    return data


def normalize_headers(table: Any) -> tuple[tuple[str, str], ...]:
    """Parse [headers] table into an immutable sequence of (name, value) pairs."""
    if table is None:
        return ()
    if not isinstance(table, Mapping):
        raise ValueError("[headers] must be a table of string keys and string values")
    out: list[tuple[str, str]] = []
    for key, raw in table.items():
        name = str(key).strip()
        if not name:
            raise ValueError("[headers]: empty header name")
        value = "" if raw is None else str(raw)
        out.append((name, value))
    return tuple(out)
