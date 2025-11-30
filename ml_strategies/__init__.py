"""Machine learning and heuristic strategies for EuroMillions generation."""

from .frequency_strategy import run_strategy as frequency_strategy
from .random_strategy import run_strategy as random_strategy

__all__ = [
    "frequency_strategy",
    "random_strategy",
]
