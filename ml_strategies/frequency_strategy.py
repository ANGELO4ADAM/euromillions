from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence


def run_strategy(game_profile: Dict, draw_history: Sequence[Dict]) -> Dict:
    """Generate numbers based on historical frequency.

    Args:
        game_profile: Metadata describing the game ranges and counts.
        draw_history: Iterable of past draw dictionaries with "numbers" and "stars".

    Returns:
        A dictionary containing the generated "numbers", "stars", "confidence_score",
        "method_used" and an "explanation".
    """

    numbers_counter: Counter[int] = Counter()
    stars_counter: Counter[int] = Counter()
    for draw in draw_history:
        numbers_counter.update(draw.get("numbers", []))
        stars_counter.update(draw.get("stars", []))

    def _top_elements(counter: Counter, count: int, fallback_range: range) -> List[int]:
        if not counter:
            return list(fallback_range)[:count]
        ordered = [value for value, _ in counter.most_common()]
        if len(ordered) >= count:
            return ordered[:count]
        missing = [n for n in fallback_range if n not in counter]
        return (ordered + missing)[:count]

    numbers_range = range(1, game_profile.get("max_number", 50) + 1)
    stars_range = range(1, game_profile.get("max_star", 12) + 1)

    numbers = _top_elements(numbers_counter, game_profile.get("numbers_to_pick", 5), numbers_range)
    stars = _top_elements(stars_counter, game_profile.get("stars_to_pick", 2), stars_range)

    confidence_score = 0.7 if numbers_counter and stars_counter else 0.4
    explanation = (
        "Sélection basée sur les numéros et étoiles les plus fréquents dans l'historique." \
        if numbers_counter and stars_counter else
        "Historique insuffisant : utilisation des premières valeurs disponibles."
    )

    return {
        "numbers": numbers,
        "stars": stars,
        "confidence_score": confidence_score,
        "method_used": "frequency",
        "explanation": explanation,
    }
