from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List


def _store_path() -> Path:
    override = os.environ.get("MANUAL_DRAWS_PATH")
    if override:
        return Path(override)
    return Path(__file__).parent / "data" / "manual_draws.json"


def _training_status_path() -> Path:
    override = os.environ.get("TRAINING_STATUS_PATH")
    if override:
        return Path(override)
    return Path(__file__).parent / "data" / "training_status.json"


def load_store() -> Dict[str, List[Dict[str, object]]]:
    path = _store_path()
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return {}
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(v, list)}


def export_store() -> Dict[str, List[Dict[str, object]]]:
    """Return the full persisted store for backup/inspection purposes."""

    return load_store()


def save_store(store: Dict[str, List[Dict[str, object]]]) -> Dict[str, List[Dict[str, object]]]:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return store


def load_training_status() -> Dict[str, object]:
    """Return the training status file (or defaults)."""

    path = _training_status_path()
    if not path.exists():
        return {"last_mode": None, "last_triggered_at": None, "runs": []}
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return {"last_mode": None, "last_triggered_at": None, "runs": []}
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {"last_mode": None, "last_triggered_at": None, "runs": []}
    if not isinstance(data, dict):
        return {"last_mode": None, "last_triggered_at": None, "runs": []}
    runs = data.get("runs", []) if isinstance(data.get("runs"), list) else []
    return {
        "last_mode": data.get("last_mode"),
        "last_triggered_at": data.get("last_triggered_at"),
        "runs": runs,
    }


def save_training_status(status: Dict[str, object]) -> Dict[str, object]:
    path = _training_status_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
    return status


def record_training_run(mode: str, *, source: str | None = None, note: str | None = None) -> Dict[str, object]:
    """Persist a lightweight training trigger and return the new status."""

    now = datetime.utcnow().isoformat() + "Z"
    status = load_training_status()
    run_entry = {"mode": mode, "source": source, "note": note, "triggered_at": now}
    status.setdefault("runs", []).append(run_entry)
    status["last_mode"] = mode
    status["last_triggered_at"] = now
    return save_training_status(status)


def append_draws(game: str, draws: List[Dict[str, object]]) -> List[Dict[str, object]]:
    store = load_store()
    normalized_key = game.lower()
    game_draws = store.get(normalized_key, [])
    game_draws.extend(draws)
    store[normalized_key] = game_draws
    save_store(store)
    return game_draws


def persist_draws(game: str, draws: List[Dict[str, object]], *, replace: bool = False) -> List[Dict[str, object]]:
    """Append or replace draws for the given game and persist to disk."""

    store = load_store()
    normalized_key = game.lower()
    if replace:
        store[normalized_key] = list(draws)
    else:
        store[normalized_key] = store.get(normalized_key, []) + list(draws)
    save_store(store)
    return store[normalized_key]


def clear_draws(game: str) -> bool:
    """Remove all draws for a given game. Returns True if something was deleted."""

    store = load_store()
    normalized_key = game.lower()
    deleted = normalized_key in store
    store.pop(normalized_key, None)
    save_store(store)
    return deleted


def get_draws(game: str) -> List[Dict[str, object]]:
    store = load_store()
    return store.get(game.lower(), [])


def summarize_store() -> Dict[str, Dict[str, object]]:
    """Return a summary of the stored manual draws per game."""

    store = load_store()
    summary: Dict[str, Dict[str, object]] = {}
    for game, draws in store.items():
        last_date = None
        for draw in draws:
            draw_date = draw.get("draw_date") if isinstance(draw, dict) else None
            if not draw_date:
                continue
            try:
                parsed = date.fromisoformat(str(draw_date))
            except ValueError:
                continue
            last_date = parsed if last_date is None or parsed > last_date else last_date

        summary[game] = {
            "stored": len(draws),
            "last_draw_date": last_date.isoformat() if last_date else None,
        }
    return summary
