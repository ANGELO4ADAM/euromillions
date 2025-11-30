from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence


FIBO_INTERVALS = [1, 2, 3, 5, 8, 13]


def _pick_top(counter: Counter[int], count: int, pool: range) -> List[int]:
    if not counter:
        return list(pool)[:count]
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    selected = [value for value, _ in ordered[:count]]
    if len(selected) < count:
        missing = [n for n in pool if n not in counter]
        selected.extend(missing[: count - len(selected)])
    return selected


def run_strategy(game_profile: Dict, draw_history: Sequence[Dict]) -> Dict:
    """Fibonacci inversé: exploite des tirages espacés selon la suite de Fibonacci."""

    numbers_counter: Counter[int] = Counter()
    stars_counter: Counter[int] = Counter()

    for interval in FIBO_INTERVALS:
        if interval <= len(draw_history):
            draw = draw_history[-interval]
            numbers_counter.update(draw.get("numbers", []))
            stars_counter.update(draw.get("stars", []))

    numbers_range = range(1, game_profile.get("max_number", 50) + 1)
    stars_range = range(1, game_profile.get("max_star", 12) + 1)

    numbers = _pick_top(numbers_counter, game_profile.get("numbers_to_pick", 5), numbers_range)
    stars = _pick_top(stars_counter, game_profile.get("stars_to_pick", 2), stars_range)

    explanation = (
        "Fibonacci inversé : sélection des valeurs récurrentes aux intervalles 1,2,3,5,8,13 tirages."
        if numbers_counter or stars_counter
        else "Historique insuffisant : sélection des premiers numéros et étoiles disponibles."
    )

    return {
        "numbers": numbers,
        "stars": stars,
        "confidence_score": 0.55 if numbers_counter or stars_counter else 0.35,
        "method_used": "fibo",
        "explanation": explanation,
    }
