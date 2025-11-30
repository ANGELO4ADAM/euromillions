from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List


def _store_path() -> Path:
    override = os.environ.get("MANUAL_DRAWS_PATH")
    if override:
        return Path(override)
    return Path(__file__).parent / "data" / "manual_draws.json"


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


def save_store(store: Dict[str, List[Dict[str, object]]]) -> Dict[str, List[Dict[str, object]]]:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return store


def append_draws(game: str, draws: List[Dict[str, object]]) -> List[Dict[str, object]]:
    store = load_store()
    normalized_key = game.lower()
    game_draws = store.get(normalized_key, [])
    game_draws.extend(draws)
    store[normalized_key] = game_draws
    save_store(store)
    return game_draws


def get_draws(game: str) -> List[Dict[str, object]]:
    store = load_store()
    return store.get(game.lower(), [])
