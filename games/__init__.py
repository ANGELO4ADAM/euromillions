"""Centralise les univers pour l'API et les workers."""

from games.registry import GAME_PROFILES, get_profile, resolve_game

__all__ = ["GAME_PROFILES", "get_profile", "resolve_game"]
