"""HTTP client for the TaskForce API v2 (`/api/v1/tasks`).

All requests use a shared :class:`requests.Session` with a mandatory
timeout so the GUI never hangs indefinitely (e.g. Render cold start).
Error responses follow the API contract ``{"detail": ..., "code": ...}``.
"""

from __future__ import annotations

from typing import Any, Optional

import requests

from config import API_URL as DEFAULT_API_URL
from config import TIMEOUT as DEFAULT_TIMEOUT
from config import normalize_api_url


class ApiError(Exception):
    """Structured API/transport failure shown to the user."""

    def __init__(
        self,
        message: str,
        status: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


class TaskForceClient:
    """Thin wrapper over the TaskForce API v2 endpoints."""

    def __init__(
        self,
        base_url: str = DEFAULT_API_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = normalize_api_url(base_url or DEFAULT_API_URL)
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _wrong_endpoint_hint(self, what: str) -> str:
        return (
            f"Resposta inesperada da API ao buscar {what}. "
            f"Verifique se a URL aponta para o endpoint de tarefas "
            f"(.../api/v1/tasks). Base atual: {self.base_url}"
        )

    # -- internals -----------------------------------------------------
    def _url(self, *parts: str) -> str:
        suffix = "".join(f"/{str(p).strip('/')}" for p in parts if str(p) != "")
        return f"{self.base_url}{suffix}"

    def _request(self, method: str, url: str, **kwargs: Any) -> Any | None:
        kwargs.setdefault("timeout", self.timeout)
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.Timeout as exc:
            raise ApiError(
                "Tempo esgotado: a API demorou a responder "
                "(pode ser cold start no Render). Tente novamente."
            ) from exc
        except requests.ConnectionError as exc:
            raise ApiError(
                "Não foi possível conectar à API. "
                "Verifique se ela está no ar e a URL configurada."
            ) from exc
        except requests.RequestException as exc:
            raise ApiError(f"Falha de rede: {exc}") from exc

        if response.status_code == 204:
            return None
        try:
            payload: Any = response.json()
        except ValueError:
            payload = None

        if 200 <= response.status_code < 300:
            return payload

        detail = "Erro inesperado da API."
        code: str | None = None
        if isinstance(payload, dict):
            raw_detail = payload.get("detail", detail)
            code = payload.get("code")
            if isinstance(raw_detail, list):
                # FastAPI/Pydantic 422 validation errors.
                bits = []
                for err in raw_detail:
                    if isinstance(err, dict):
                        loc = ".".join(str(x) for x in err.get("loc", []))
                        bits.append(f"{loc}: {err.get('msg', '')}".strip(": "))
                detail = "; ".join(bits) if bits else detail
            elif raw_detail:
                detail = str(raw_detail)
        elif response.text:
            detail = response.text[:300]
        raise ApiError(detail, status=response.status_code, code=code)

    # -- endpoints ------------------------------------------------------
    def list_tasks(
        self,
        search: Optional[str] = None,
        is_done: Optional[bool] = None,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        """GET /api/v1/tasks -> {items, total, page, size, pages}."""
        params: dict[str, Any] = {"page": max(1, page), "size": max(1, min(size, 100))}
        if search and search.strip():
            params["search"] = search.strip()[:100]
        if is_done is not None:
            params["is_done"] = str(bool(is_done)).lower()
        data = self._request("GET", self._url(""), params=params)
        if not isinstance(data, dict) or "items" not in data:
            raise ApiError(self._wrong_endpoint_hint("tarefas"))
        data.setdefault("items", [])
        return data

    def stats(self) -> dict[str, Any]:
        """GET /api/v1/tasks/stats -> {total, done, pending}."""
        data = self._request("GET", self._url("stats"))
        if not isinstance(data, dict) or "total" not in data:
            raise ApiError(self._wrong_endpoint_hint("estatísticas"))
        return data

    def create(self, title: str) -> dict[str, Any]:
        """POST /api/v1/tasks with JSON body {"title": ...}."""
        cleaned = (title or "").strip()
        if not cleaned:
            raise ApiError("Digite o título da tarefa.", status=None)
        if len(cleaned) > 200:
            raise ApiError("Título muito longo (máximo 200 caracteres).", status=None)
        data = self._request("POST", self._url(""), json={"title": cleaned})
        if not isinstance(data, dict):
            raise ApiError("Resposta inválida da API ao criar tarefa.")
        return data

    def get(self, task_id: int) -> dict[str, Any]:
        data = self._request("GET", self._url(int(task_id)))
        if not isinstance(data, dict):
            raise ApiError("Resposta inválida da API ao buscar tarefa.")
        return data

    def toggle_done(self, task_id: int) -> dict[str, Any]:
        """PATCH /api/v1/tasks/{id}/done (toggle)."""
        data = self._request("PATCH", self._url(int(task_id), "done"))
        if not isinstance(data, dict):
            raise ApiError("Resposta inválida da API ao alternar tarefa.")
        return data

    def update(
        self,
        task_id: int,
        title: Optional[str] = None,
        done: Optional[bool] = None,
    ) -> dict[str, Any]:
        """PATCH /api/v1/tasks/{id} with {"title"?, "done"?}."""
        body: dict[str, Any] = {}
        if title is not None:
            cleaned = title.strip()
            if not cleaned:
                raise ApiError("O título não pode ficar em branco.", status=None)
            if len(cleaned) > 200:
                raise ApiError("Título muito longo (máximo 200 caracteres).", status=None)
            body["title"] = cleaned
        if done is not None:
            body["done"] = bool(done)
        if not body:
            raise ApiError("Nada para atualizar.", status=None)
        data = self._request("PATCH", self._url(int(task_id)), json=body)
        if not isinstance(data, dict):
            raise ApiError("Resposta inválida da API ao atualizar tarefa.")
        return data

    def delete(self, task_id: int) -> None:
        """DELETE /api/v1/tasks/{id} -> 204 (no content)."""
        self._request("DELETE", self._url(int(task_id)))
        return None
