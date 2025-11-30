from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence


SHORT_WINDOW = 20
LONG_WINDOW = 120


def _compute_score(short_counter: Counter[int], long_counter: Counter[int], value: int) -> float:
    short_freq = short_counter.get(value, 0)
    long_freq = long_counter.get(value, 0)
    if long_freq == 0:
        return -1.0  # absent du long terme
    # score élevé si valeur présente au long terme mais absente/réduite récemment
    return (long_freq - short_freq) + (0.5 if short_freq == 0 else 0.0)


def _select_values(short_counter: Counter[int], long_counter: Counter[int], pool: range, count: int) -> List[int]:
    scored = []
    for value in pool:
        score = _compute_score(short_counter, long_counter, value)
        scored.append((score, value))
    scored.sort(key=lambda item: (-item[0], item[1]))
    selected = [value for _, value in scored[:count]]
    return selected


def run_strategy(game_profile: Dict, draw_history: Sequence[Dict]) -> Dict:
    """SPECTRE IA : contraste des tendances court terme vs long terme."""

    short_draws = draw_history[-SHORT_WINDOW:]
    long_draws = draw_history[-LONG_WINDOW:]

    short_numbers: Counter[int] = Counter()
    short_stars: Counter[int] = Counter()
    long_numbers: Counter[int] = Counter()
    long_stars: Counter[int] = Counter()

    for draw in short_draws:
        short_numbers.update(draw.get("numbers", []))
        short_stars.update(draw.get("stars", []))

    for draw in long_draws:
        long_numbers.update(draw.get("numbers", []))
        long_stars.update(draw.get("stars", []))

    numbers_range = range(1, game_profile.get("max_number", 50) + 1)
    stars_range = range(1, game_profile.get("max_star", 12) + 1)

    numbers = _select_values(short_numbers, long_numbers, numbers_range, game_profile.get("numbers_to_pick", 5))
    stars = _select_values(short_stars, long_stars, stars_range, game_profile.get("stars_to_pick", 2))

    has_history = bool(long_draws)
    explanation = (
        "SPECTRE IA : contraste fréquence long terme (120) vs court terme (20) pour repérer les retours probables."
        if has_history
        else "Historique insuffisant : classement par ordre naturel faute de contraste temporel."
    )

    return {
        "numbers": numbers,
        "stars": stars,
        "confidence_score": 0.6 if has_history else 0.35,
        "method_used": "spectre",
        "explanation": explanation,
    }
