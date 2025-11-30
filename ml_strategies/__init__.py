"""Machine learning and heuristic strategies for EuroMillions generation."""

from .fibo import run_strategy as fibo_strategy
from .frequency_strategy import run_strategy as frequency_strategy
from .mcc import run_strategy as mcc_strategy
from .meta_ia import run_strategy as meta_ia_strategy
from .random_strategy import run_strategy as random_strategy
from .spectre import run_strategy as spectre_strategy

__all__ = [
    "fibo_strategy",
    "frequency_strategy",
    "mcc_strategy",
    "meta_ia_strategy",
    "random_strategy",
    "spectre_strategy",
]
