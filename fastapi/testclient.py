from __future__ import annotations

import inspect
from typing import Any, Dict

from . import FastAPI, HTTPException


class Response:
    def __init__(self, status_code: int, content: Any):
        self.status_code = status_code
        self._content = content

    def json(self) -> Any:
        if hasattr(self._content, "model_dump"):
            return self._content.model_dump()
        return self._content


class TestClient:
    def __init__(self, app: FastAPI):
        self.app = app

    def _build_body_arg(self, func: Any, param: inspect.Parameter, payload: Dict[str, Any] | None) -> Any:
        if payload is None:
            return None
        annotation = param.annotation
        if isinstance(annotation, str):
            annotation = func.__globals__.get(annotation, annotation)
        try:
            if inspect.isclass(annotation):
                return annotation(**payload)
        except Exception:
            pass
        return payload

    def _call(self, method: str, path: str, json: Dict[str, Any] | None = None) -> Response:
        try:
            func, path_params = self.app.resolve(method, path)
            sig = inspect.signature(func)
            kwargs: Dict[str, Any] = {}
            for name, param in sig.parameters.items():
                if name in path_params:
                    kwargs[name] = path_params[name]
                else:
                    kwargs[name] = self._build_body_arg(func, param, json)
            result = func(**kwargs)
            status_code = 200
            content = result
        except HTTPException as exc:
            status_code = exc.status_code
            content = {"detail": exc.detail}
        return Response(status_code=status_code, content=content)

    def post(self, path: str, json: Dict[str, Any] | None = None) -> Response:
        return self._call("POST", path, json)

    def get(self, path: str) -> Response:
        return self._call("GET", path)
