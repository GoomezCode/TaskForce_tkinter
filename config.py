"""Central configuration for the TaskForce Tkinter client.

Resolution order for each setting:
1. Environment variable (highest priority)
2. `.env` file next to this module (minimal parser, no extra dependency)
3. Built-in fallback (production API v2)

Env vars:
    TASKFORCE_API_URL   Base URL of the tasks API. The API root alone is
                        accepted and normalized (see `normalize_api_url`).
                        e.g. https://taskforce-api-zxag.onrender.com/api/v1/tasks
                        Local dev: http://localhost:8000/api/v1/tasks
    TASKFORCE_TIMEOUT   HTTP timeout in seconds (default: 10)
    TASKFORCE_PAGE_SIZE Default page size for listing (default: 20)
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

_HOST_RE = re.compile(r"^[\w.-]+(:\d+)?$")

TASKS_PATH = "/api/v1/tasks"
DEFAULT_API_URL = f"https://taskforce-api-zxag.onrender.com{TASKS_PATH}"
DEFAULT_TIMEOUT = 10.0
DEFAULT_PAGE_SIZE = 20


def _load_dotenv(path: Path | None = None) -> None:
    """Minimal `.env` loader (KEY=VALUE, ignores comments/blank lines).

    Does not override variables already present in the environment.
    Silently ignores a missing file.
    """
    env_path = path or (Path(__file__).resolve().parent / ".env")
    try:
        content = env_path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()


def _parse_timeout(raw: str | None) -> float:
    try:
        value = float(raw) if raw is not None else DEFAULT_TIMEOUT
    except (TypeError, ValueError):
        return DEFAULT_TIMEOUT
    return max(1.0, min(value, 120.0))


def _parse_page_size(raw: str | None) -> int:
    try:
        value = int(raw) if raw is not None else DEFAULT_PAGE_SIZE
    except (TypeError, ValueError):
        return DEFAULT_PAGE_SIZE
    return max(1, min(value, 100))


def normalize_api_url(raw: str | None) -> str:
    """Normalize a user-provided API URL to the tasks endpoint.

    Accepts the API root (``https://host`` or ``https://host/``), the
    legacy ``.../task`` suffix, or the full ``.../api/v1/tasks`` URL.
    Anything else (custom path) is kept as-is, minus trailing slashes.
    Falls back to :data:`DEFAULT_API_URL` for empty/invalid values.
    """
    if not raw or not raw.strip():
        return DEFAULT_API_URL
    candidate = raw.strip()
    if "://" not in candidate:
        candidate = f"http://{candidate}"
    try:
        parts = urlsplit(candidate)
    except ValueError:
        return DEFAULT_API_URL
    if not parts.netloc or not _HOST_RE.match(parts.netloc):
        return DEFAULT_API_URL
    path = parts.path.rstrip("/")
    if path in ("", "/"):
        path = TASKS_PATH
    elif path == "/task":
        path = TASKS_PATH
    normalized = urlunsplit((parts.scheme, parts.netloc, path, "", ""))
    return normalized


API_URL: str = normalize_api_url(os.getenv("TASKFORCE_API_URL", DEFAULT_API_URL))
TIMEOUT: float = _parse_timeout(os.getenv("TASKFORCE_TIMEOUT"))
PAGE_SIZE: int = _parse_page_size(os.getenv("TASKFORCE_PAGE_SIZE"))
