"""
Tiny zero-dependency .env loader and typed environment readers.

Keeping this in the project avoids pulling in an extra package just to read a
handful of variables. A `.env` file sitting next to manage.py is loaded once at
import time; real process environment variables always win over the file, which
is what you want on a PaaS where secrets are injected by the platform.
"""

from __future__ import annotations

import os
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BASE_DIR / ".env"

_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off", ""}


def _load_env_file(path: Path = _ENV_FILE) -> None:
    """Populate os.environ from a KEY=VALUE file without overriding real vars."""
    if not path.is_file():
        return
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return

    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


_load_env_file()


def env_str(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    return default if value is None else value.strip()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    value = value.strip().lower()
    if value in _TRUTHY:
        return True
    if value in _FALSY:
        return False
    return default


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "").strip())
    except (TypeError, ValueError):
        return default


def env_list(name: str, default: list[str] | None = None) -> list[str]:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]
