"""Backward-compatibility shim for the old ``utilTask`` function API.

.. deprecated::
    Import from :mod:`api.client` (:class:`TaskForceClient`) instead.
    This module is kept only so old imports don't break; it now talks
    to the API v2 endpoints.
"""

from __future__ import annotations

from typing import Any

import config
from api.client import TaskForceClient

_client = TaskForceClient(base_url=config.API_URL, timeout=config.TIMEOUT)


def getTask(search: str | None = None) -> list[dict[str, Any]]:
    """Return the first page of tasks as a plain list (legacy shape)."""
    data = _client.list_tasks(search=search, size=config.PAGE_SIZE)
    return data.get("items", [])


def createTask(nmTarefa: str) -> dict[str, Any]:
    """Create a task; returns the created task dict (raises ApiError on failure)."""
    return _client.create(nmTarefa)


def deleteTask(idTask: int | str) -> None:
    """Delete a task by id (raises ApiError on failure)."""
    _client.delete(int(idTask))


def marcarTask(idTask: int | str) -> dict[str, Any]:
    """Toggle a task's done status (raises ApiError on failure)."""
    return _client.toggle_done(int(idTask))
