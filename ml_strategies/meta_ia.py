from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence

from .fibo import run_strategy as fibo_strategy
from .mcc import run_strategy as mcc_strategy
from .spectre import run_strategy as spectre_strategy


def _consensus(values: List[List[int]], pool: range, count: int) -> List[int]:
    counter: Counter[int] = Counter()
    for proposal in values:
        counter.update(proposal)
    if not counter:
        return list(pool)[:count]
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    selected = [value for value, _ in ordered[:count]]
    if len(selected) < count:
        missing = [n for n in pool if n not in counter]
        selected.extend(missing[: count - len(selected)])
    return selected


def run_strategy(game_profile: Dict, draw_history: Sequence[Dict]) -> Dict:
    """META IA : consensus des stratégies FIBO, MCC et SPECTRE."""

    fibo = fibo_strategy(game_profile, draw_history)
    mcc = mcc_strategy(game_profile, draw_history)
    spectre = spectre_strategy(game_profile, draw_history)

    numbers_range = range(1, game_profile.get("max_number", 50) + 1)
    stars_range = range(1, game_profile.get("max_star", 12) + 1)

    numbers = _consensus([fibo["numbers"], mcc["numbers"], spectre["numbers"]], numbers_range, game_profile.get("numbers_to_pick", 5))
    stars = _consensus([fibo["stars"], mcc["stars"], spectre["stars"]], stars_range, game_profile.get("stars_to_pick", 2))

    explanation = (
        "META IA : consensus entre FIBO, MCC et SPECTRE pour stabiliser les propositions."
    )

    avg_confidence = (fibo["confidence_score"] + mcc["confidence_score"] + spectre["confidence_score"]) / 3

    return {
        "numbers": numbers,
        "stars": stars,
        "confidence_score": round(avg_confidence, 2),
        "method_used": "meta_ia",
        "explanation": explanation,
    }
