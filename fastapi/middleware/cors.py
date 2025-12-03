"""CORS middleware stub to align with FastAPI surface used in the project."""

from __future__ import annotations

from typing import Any, Iterable, List


class CORSMiddleware:
    def __init__(
        self,
        app: Any,
        allow_origins: Iterable[str] | None = None,
        allow_methods: Iterable[str] | None = None,
        allow_headers: Iterable[str] | None = None,
    ):
        self.app = app
        self.allow_origins: List[str] = list(allow_origins or [])
        self.allow_methods: List[str] = list(allow_methods or [])
        self.allow_headers: List[str] = list(allow_headers or [])


__all__ = ["CORSMiddleware"]
