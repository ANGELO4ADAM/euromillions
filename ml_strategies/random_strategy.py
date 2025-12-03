from __future__ import annotations

import random
from typing import Dict, Sequence


def run_strategy(game_profile: Dict, draw_history: Sequence[Dict]) -> Dict:
    """Generate numbers by shuffling the allowed ranges.

    Args:
        game_profile: Metadata describing the game ranges and counts.
        draw_history: Iterable of past draw dictionaries. Unused but kept for signature.

    Returns:
        A dictionary containing the generated "numbers", "stars", "confidence_score",
        "method_used" and an "explanation".
    """

    numbers_range = list(range(1, game_profile.get("max_number", 50) + 1))
    stars_range = list(range(1, game_profile.get("max_star", 12) + 1))

    random.shuffle(numbers_range)
    random.shuffle(stars_range)

    numbers = sorted(numbers_range[: game_profile.get("numbers_to_pick", 5)])
    stars = sorted(stars_range[: game_profile.get("stars_to_pick", 2)])

    return {
        "numbers": numbers,
        "stars": stars,
        "confidence_score": 0.2,
        "method_used": "random",
        "explanation": "Sélection entièrement aléatoire dans les plages autorisées.",
    }
