from __future__ import annotations

from typing import Any, Callable, Dict


class FieldInfo:
    def __init__(self, default: Any = None, default_factory: Callable[[], Any] | None = None, description: str | None = None):
        self.default = default
        self.default_factory = default_factory
        self.description = description


def Field(default: Any = None, *, default_factory: Callable[[], Any] | None = None, description: str | None = None) -> FieldInfo:
    return FieldInfo(default=default, default_factory=default_factory, description=description)


class BaseModel:
    def __init__(self, **data: Any):
        annotations = getattr(self, "__annotations__", {})
        for name in annotations:
            if name in data:
                value = data[name]
            else:
                field_info = getattr(self.__class__, name, None)
                if isinstance(field_info, FieldInfo):
                    if field_info.default_factory is not None:
                        value = field_info.default_factory()
                    else:
                        value = field_info.default
                else:
                    value = field_info
            setattr(self, name, value)

    def model_dump(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        annotations = getattr(self, "__annotations__", {})
        for name in annotations:
            value = getattr(self, name, None)
            if isinstance(value, BaseModel):
                result[name] = value.model_dump()
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                result[name] = [item.model_dump() for item in value]
            else:
                result[name] = value
        return result


__all__ = ["BaseModel", "Field"]
