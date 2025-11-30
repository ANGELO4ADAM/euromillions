from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence


WINDOW = 80


def _least_frequent(counter: Counter[int], count: int, pool: range) -> List[int]:
    if not counter:
        return list(pool)[:count]
    ordered = sorted(counter.items(), key=lambda item: (item[1], item[0]))
    selected = [value for value, _ in ordered[:count]]
    if len(selected) < count:
        missing = [n for n in pool if n not in counter]
        selected.extend(missing[: count - len(selected)])
    return selected


def run_strategy(game_profile: Dict, draw_history: Sequence[Dict]) -> Dict:
    """Monte Carlo combinatoire: favorise les valeurs les moins sorties récemment."""

    recent_draws = draw_history[-WINDOW:]
    numbers_counter: Counter[int] = Counter()
    stars_counter: Counter[int] = Counter()

    for draw in recent_draws:
        numbers_counter.update(draw.get("numbers", []))
        stars_counter.update(draw.get("stars", []))

    numbers_range = range(1, game_profile.get("max_number", 50) + 1)
    stars_range = range(1, game_profile.get("max_star", 12) + 1)

    numbers = _least_frequent(numbers_counter, game_profile.get("numbers_to_pick", 5), numbers_range)
    stars = _least_frequent(stars_counter, game_profile.get("stars_to_pick", 2), stars_range)

    explanation = (
        "Monte Carlo combinatoire : pondération inversée sur les 80 derniers tirages pour privilégier les numéros en retard."
        if recent_draws
        else "Historique insuffisant : sélection des premiers numéros et étoiles disponibles."
    )

    return {
        "numbers": numbers,
        "stars": stars,
        "confidence_score": 0.5 if recent_draws else 0.3,
        "method_used": "mcc",
        "explanation": explanation,
    }
