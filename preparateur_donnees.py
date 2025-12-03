from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Sequence


def _sliding_windows(sequence: Sequence[int], window_size: int) -> List[List[int]]:
    return [list(sequence[i : i + window_size]) for i in range(len(sequence) - window_size + 1)]


def calculate_frequencies(draw_history: Iterable[Dict]) -> Dict[str, Counter]:
    numbers_counter: Counter[int] = Counter()
    stars_counter: Counter[int] = Counter()
    for draw in draw_history:
        numbers_counter.update(draw.get("numbers", []))
        stars_counter.update(draw.get("stars", []))
    return {"numbers": numbers_counter, "stars": stars_counter}


def calculate_gaps(draw_history: Iterable[Dict], game_profile: Dict) -> Dict[str, Dict[int, int]]:
    max_number = game_profile.get("max_number", 50)
    max_star = game_profile.get("max_star", 12)
    gaps_numbers = {n: 0 for n in range(1, max_number + 1)}
    gaps_stars = {s: 0 for s in range(1, max_star + 1)}

    for draw in draw_history:
        present_numbers = set(draw.get("numbers", []))
        present_stars = set(draw.get("stars", []))
        gaps_numbers = {n: (0 if n in present_numbers else gaps_numbers[n] + 1) for n in gaps_numbers}
        gaps_stars = {s: (0 if s in present_stars else gaps_stars[s] + 1) for s in gaps_stars}

    return {"numbers": gaps_numbers, "stars": gaps_stars}


def prepare_features(game_profile: Dict, draw_history: Sequence[Dict], window_size: int = 5) -> Dict:
    """Compute frequency, gaps and sliding window aggregates for a game.

    Args:
        game_profile: Metadata describing the game ranges and counts.
        draw_history: Ordered list of draws, newest last.
        window_size: Size of the sliding window to compute local frequencies.

    Returns:
        Dictionary with keys "global_frequencies", "gaps", "windows".
    """

    frequencies = calculate_frequencies(draw_history)
    gaps = calculate_gaps(draw_history, game_profile)
    numbers_windows = _sliding_windows(
        [n for draw in draw_history for n in draw.get("numbers", [])], window_size
    ) if draw_history else []
    stars_windows = _sliding_windows(
        [s for draw in draw_history for s in draw.get("stars", [])], window_size
    ) if draw_history else []

    return {
        "global_frequencies": frequencies,
        "gaps": gaps,
        "windows": {
            "numbers": numbers_windows,
            "stars": stars_windows,
        },
    }
