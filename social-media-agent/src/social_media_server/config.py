"""Credential loading.

Reads a `.env` file sitting next to the project root (if present) and falls
back to the process environment. No third-party dependency required.
"""

from __future__ import annotations

import os
from pathlib import Path


def _project_root() -> Path:
    # config.py lives at src/social_media_server/config.py -> root is three up.
    return Path(__file__).resolve().parents[2]


def load_env() -> None:
    """Populate os.environ from a sibling .env file without overriding real env vars."""
    env_path = _project_root() / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get(name: str) -> str | None:
    value = os.environ.get(name)
    return value if value else None
