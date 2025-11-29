"""Registre centralisé des univers de jeu pour clarifier l'architecture."""
from typing import Dict

from games.euromillions import PROFILE as EUROMILLIONS_PROFILE
from games.eurodream import PROFILE as EURODREAM_PROFILE

GAME_PROFILES: Dict[str, Dict[str, int]] = {
    EUROMILLIONS_PROFILE["key"]: EUROMILLIONS_PROFILE,
    EURODREAM_PROFILE["key"]: EURODREAM_PROFILE,
}


def resolve_game(raw: str | None) -> str:
    """Normalise le nom du jeu et applique un défaut robuste."""
    game = (raw or "euromillions").lower()
    return game if game in GAME_PROFILES else "euromillions"


def get_profile(game: str) -> Dict[str, int]:
    """Récupère le profil associé à un jeu après résolution sécurisée."""
    normalized = resolve_game(game)
    return GAME_PROFILES.get(normalized, GAME_PROFILES["euromillions"])
