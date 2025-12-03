from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

DEFAULT_MODELS = ["atlas-v1", "orion-v2", "vega-targeted"]


def _admin_state_path() -> Path:
    override = os.environ.get("ADMIN_STATE_PATH")
    if override:
        return Path(override)
    return Path(__file__).parent / "data" / "admin_state.json"


def _default_state() -> Dict[str, object]:
    return {
        "ai_models": list(DEFAULT_MODELS),
        "deleted_models": [],
        "ai_history": [],
        "logs": {"backend": "", "celery": "", "ia": ""},
        "celery_status": {
            "workers": 2,
            "status": "online",
            "tasks": 0,
            "queueLength": 0,
            "avgDuration": "—",
        },
        "system_health": {"cpu": "12%", "ram": "45%", "disk": "38%", "status": "green"},
        "last_panic": None,
    }


def load_admin_state() -> Dict[str, object]:
    path = _admin_state_path()
    if not path.exists():
        return _default_state()
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return _default_state()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return _default_state()
    if not isinstance(data, dict):
        return _default_state()
    # Ensure required keys
    default = _default_state()
    for key, value in default.items():
        data.setdefault(key, value)
    return data


def save_admin_state(state: Dict[str, object]) -> Dict[str, object]:
    path = _admin_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state


def get_ai_models() -> List[str]:
    state = load_admin_state()
    return state.get("ai_models", [])


def delete_ai_model(model: str) -> List[str]:
    state = load_admin_state()
    models = state.get("ai_models", [])
    if model in models:
        models.remove(model)
        deleted = state.get("deleted_models", [])
        deleted.append(model)
        state["ai_models"] = models
        state["deleted_models"] = deleted
        save_admin_state(state)
    return state.get("ai_models", [])


def restore_ai_model(model: str | None = None) -> List[str]:
    state = load_admin_state()
    deleted = state.get("deleted_models", [])
    target = model or (deleted[-1] if deleted else None)
    if target and target not in state.get("ai_models", []):
        state.setdefault("ai_models", []).append(target)
        state["deleted_models"] = [m for m in deleted if m != target]
        save_admin_state(state)
    return state.get("ai_models", [])


def record_ai_history(model: str, *, score: float | None = None, rmse: float | None = None,
                      accuracy: float | None = None, duration: str | None = None) -> List[Dict[str, object]]:
    state = load_admin_state()
    history: List[Dict[str, object]] = state.get("ai_history", [])
    entry = {
        "id": str(uuid4()),
        "date": datetime.utcnow().isoformat() + "Z",
        "duration": duration or "~5m",
        "model": model,
        "score": score if score is not None else 0.0,
        "rmse": rmse if rmse is not None else score if score is not None else 0.0,
        "accuracy": accuracy if accuracy is not None else 0.0,
        "internal": score if score is not None else 0.0,
    }
    history.insert(0, entry)
    state["ai_history"] = history[:50]
    save_admin_state(state)
    return state["ai_history"]


def get_ai_history() -> List[Dict[str, object]]:
    state = load_admin_state()
    return state.get("ai_history", [])


def get_logs() -> Dict[str, str]:
    state = load_admin_state()
    return state.get("logs", {})


def set_logs(backend: str = "", celery: str = "", ia: str = "") -> Dict[str, str]:
    state = load_admin_state()
    state["logs"] = {"backend": backend, "celery": celery, "ia": ia}
    save_admin_state(state)
    return state["logs"]


def append_log(log_type: str, message: str) -> Dict[str, str]:
    state = load_admin_state()
    logs = state.get("logs", {})
    previous = logs.get(log_type, "")
    logs[log_type] = (previous + "\n" + message).strip()
    state["logs"] = logs
    save_admin_state(state)
    return logs


def clear_logs() -> Dict[str, str]:
    return set_logs("", "", "")


def get_celery_status() -> Dict[str, object]:
    state = load_admin_state()
    return state.get("celery_status", {})


def update_celery_status(**kwargs: object) -> Dict[str, object]:
    state = load_admin_state()
    current = state.get("celery_status", {})
    current.update(kwargs)
    state["celery_status"] = current
    save_admin_state(state)
    return current


def get_system_health() -> Dict[str, object]:
    state = load_admin_state()
    return state.get("system_health", {})


def update_system_health(**kwargs: object) -> Dict[str, object]:
    state = load_admin_state()
    current = state.get("system_health", {})
    current.update(kwargs)
    state["system_health"] = current
    save_admin_state(state)
    return current


def record_panic() -> Dict[str, object]:
    state = load_admin_state()
    now = datetime.utcnow().isoformat() + "Z"
    state["last_panic"] = now
    append_log("backend", f"[panic] Safe mode enabled at {now}")
    save_admin_state(state)
    return {"status": "panic", "at": now}


def snapshot_state() -> Dict[str, object]:
    state = load_admin_state()
    return state


def restore_state(snapshot: Dict[str, object]) -> Dict[str, object]:
    return save_admin_state(snapshot)


def synthetic_stats(total_draws: int, total_grids: int, size_bytes: int, last_import: str | None = None,
                    health: str = "OK") -> Dict[str, object]:
    return {
        "totalDraws": total_draws,
        "totalGrids": total_grids,
        "dbSize": f"{size_bytes} bytes",
        "lastImport": last_import or "—",
        "dbHealth": health,
    }


