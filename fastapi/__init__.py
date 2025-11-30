"""
Lightweight FastAPI-compatible stubs for offline testing.
Only the minimal surface used by this repository is implemented.
"""
from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List, Tuple


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str | None = None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _match_path(template: str, path: str) -> Tuple[bool, Dict[str, str]]:
    template_parts = [p for p in template.strip("/").split("/") if p]
    path_parts = [p for p in path.strip("/").split("/") if p]
    if len(template_parts) != len(path_parts):
        return False, {}
    params: Dict[str, str] = {}
    for t, p in zip(template_parts, path_parts):
        if t.startswith("{") and t.endswith("}"):
            params[t.strip("{} ")] = p
        elif t != p:
            return False, {}
    return True, params


class FastAPI:
    def __init__(self, title: str | None = None):
        self.title = title
        self.routes: List[Tuple[str, str, Callable[..., Any]]] = []
        self.middleware: List[Tuple[Any, Dict[str, Any]]] = []

    def _register(self, method: str, path: str, func: Callable[..., Any]) -> Callable[..., Any]:
        self.routes.append((method.upper(), path, func))
        return func

    def get(self, path: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return self._register("GET", path, func)

        return decorator

    def post(self, path: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return self._register("POST", path, func)

        return decorator

    def delete(self, path: str, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return self._register("DELETE", path, func)

        return decorator

    def add_middleware(self, middleware_class: Any, **options: Any) -> None:
        self.middleware.append((middleware_class, options))

    def resolve(self, method: str, path: str) -> Tuple[Callable[..., Any], Dict[str, str]]:
        for registered_method, template, func in self.routes:
            if registered_method != method.upper():
                continue
            matched, params = _match_path(template, path)
            if matched:
                return func, params
        raise HTTPException(status_code=404, detail=f"Route not found: {method} {path}")


class status:
    HTTP_404_NOT_FOUND = 404
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_400_BAD_REQUEST = 400


__all__ = ["FastAPI", "HTTPException", "status"]
