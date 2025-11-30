from __future__ import annotations

from datetime import date
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import ml_strategies
from data_store import append_draws, get_draws
from preparateur_donnees import prepare_features


class Draw(BaseModel):
    numbers: List[int] = Field(default_factory=list, description="Numéros du tirage")
    stars: List[int] = Field(default_factory=list, description="Étoiles du tirage")
    draw_date: str | None = Field(
        default=None,
        description="Date du tirage au format ISO (YYYY-MM-DD) pour filtrer par jour.",
    )


class GenerateRequest(BaseModel):
    draws: List[Draw] = Field(default_factory=list, description="Historique des tirages")
    game: str = Field(default="euromillion", description="Nom du jeu ciblé")


class ManualDrawImport(BaseModel):
    game: str = Field(default="euromillion", description="Jeu ciblé")
    draws: List[Draw] = Field(default_factory=list, description="Tirages à ingérer")


class StrategyResponse(BaseModel):
    numbers: List[int]
    stars: List[int]
    confidence_score: float
    method_used: str
    explanation: str
    features: Dict[str, object]


GAME_PROFILES = {
    "euromillion": {
        "numbers_to_pick": 5,
        "stars_to_pick": 2,
        "max_number": 50,
        "max_star": 12,
    },
    "eurodream": {
        "numbers_to_pick": 5,
        "stars_to_pick": 2,
        "max_number": 50,
        "max_star": 12,
    },
}

app = FastAPI(title="EuroMillions Generator")

# Allow the static frontend (served locally or via file://) to call the API without CORS friction
if hasattr(app, "add_middleware"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Identique pour les trois jeux pour l'instant, mais la structure permet de différencier les profils plus tard.


def get_game_profile(game: str) -> Dict:
    game_key = game.lower()
    if game_key not in GAME_PROFILES:
        raise HTTPException(status_code=422, detail=f"Jeu inconnu: {game}")
    return GAME_PROFILES[game_key]


STRATEGIES = {
    "fibo": ml_strategies.fibo_strategy,
    "frequency": ml_strategies.frequency_strategy,
    "mcc": ml_strategies.mcc_strategy,
    "meta_ia": ml_strategies.meta_ia_strategy,
    "random": ml_strategies.random_strategy,
    "spectre": ml_strategies.spectre_strategy,
}


@app.get("/")
def homepage() -> Dict[str, object]:
    """Expose une page d'accueil simple avec les jeux disponibles et une mise en garde."""

    return {
        "title": "Générateur de tirages ludiques",
        "games": [
            {"name": "EUROMILLION", "description": "Tirages principaux européens"},
            {"name": "EURODREAM", "description": "Variation exploratoire"},
        ],
        "disclaimer": (
            "Ce générateur est fourni à titre ludique : il illustre des estimations sans aucune garantie de gain "
            "et aide à comprendre le comportement des tirages. Jouez de manière responsable et ne misez jamais plus "
            "que ce que vous pouvez vous permettre de perdre. "
            "This generator is for entertainment purposes only: it shows illustrative estimates with no guarantee of winning "
            "and helps visualize how draws behave. Play responsibly and never stake more than you can afford to lose."
        ),
    }


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "strategies": sorted(STRATEGIES.keys()),
        "games": sorted(GAME_PROFILES.keys()),
    }


def _validate_draw(draw: Draw, game_profile: Dict) -> None:
    numbers = draw.numbers
    stars = draw.stars
    if len(numbers) != game_profile["numbers_to_pick"] or len(stars) != game_profile["stars_to_pick"]:
        raise HTTPException(
            status_code=422,
            detail="Tirage invalide : nombre de numéros/étoiles incorrect.",
        )
    if len(set(numbers)) != len(numbers) or len(set(stars)) != len(stars):
        raise HTTPException(status_code=422, detail="Tirage invalide : doublons détectés.")
    if not all(1 <= n <= game_profile["max_number"] for n in numbers):
        raise HTTPException(status_code=422, detail="Tirage invalide : numéro hors plage.")
    if not all(1 <= s <= game_profile["max_star"] for s in stars):
        raise HTTPException(status_code=422, detail="Tirage invalide : étoile hors plage.")
    if draw.draw_date:
        try:
            date.fromisoformat(draw.draw_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="Date de tirage invalide : format attendu YYYY-MM-DD.")


def _validate_history(draws: List[Draw] | List[Dict], game_profile: Dict) -> None:
    if not draws:
        raise HTTPException(status_code=422, detail="Historique vide : impossible de générer.")
    for draw in draws:
        draw_obj = draw if isinstance(draw, Draw) else Draw(**draw)
        _validate_draw(draw_obj, game_profile)


def _normalize_draws(draws: List[Draw] | List[Dict]) -> List[Dict[str, object]]:
    normalized = []
    for draw in draws:
        draw_dict = draw.model_dump() if hasattr(draw, "model_dump") else dict(draw)
        if draw_dict.get("draw_date"):
            draw_dict["draw_date"] = date.fromisoformat(str(draw_dict["draw_date"])).isoformat()
        else:
            draw_dict.pop("draw_date", None)
        normalized.append(draw_dict)
    return normalized


def _parse_weekday(value: str) -> int:
    try:
        weekday = int(value)
    except (TypeError, ValueError):
        normalized = value.strip().lower()
        mapping = {
            "monday": 1,
            "mon": 1,
            "lundi": 1,
            "tuesday": 2,
            "tue": 2,
            "mardi": 2,
            "wednesday": 3,
            "wed": 3,
            "mercredi": 3,
            "thursday": 4,
            "thu": 4,
            "jeudi": 4,
            "friday": 5,
            "fri": 5,
            "vendredi": 5,
            "saturday": 6,
            "sat": 6,
            "samedi": 6,
            "sunday": 7,
            "sun": 7,
            "dimanche": 7,
        }
        weekday = mapping.get(normalized, 0)
    if weekday < 1 or weekday > 7:
        raise HTTPException(
            status_code=422, detail="Jour invalide : utilisez 1-7 ou un nom de jour (en/fr)."
        )
    return weekday


def _weekday_for_draw(draw: Dict[str, object]) -> int | None:
    draw_date = draw.get("draw_date") if isinstance(draw, dict) else None
    if not draw_date:
        return None
    try:
        return date.fromisoformat(str(draw_date)).isoweekday()
    except ValueError:
        return None


@app.post("/api/generate/{strategie}", response_model=StrategyResponse)
def generate(strategie: str, payload: GenerateRequest) -> StrategyResponse:
    strategy_callable = STRATEGIES.get(strategie)
    if strategy_callable is None:
        raise HTTPException(status_code=404, detail=f"Stratégie inconnue: {strategie}")

    game_profile = get_game_profile(payload.game)

    _validate_history(payload.draws, game_profile)
    draw_history = _normalize_draws(payload.draws)
    features = prepare_features(game_profile, draw_history)
    result = strategy_callable(game_profile, draw_history)

    return StrategyResponse(**result, features=features)


@app.post("/api/admin/manual-draws")
def ingest_manual_draws(payload: ManualDrawImport) -> Dict[str, object]:
    game_profile = get_game_profile(payload.game)
    _validate_history(payload.draws, game_profile)
    stored_draws = append_draws(payload.game, _normalize_draws(payload.draws))
    return {"game": payload.game.lower(), "stored": len(stored_draws)}


@app.get("/api/admin/manual-draws/{game}")
def list_manual_draws(game: str, weekday: str | None = None) -> Dict[str, object]:
    get_game_profile(game)
    draws = get_draws(game)
    if weekday is not None:
        target_weekday = _parse_weekday(weekday)
        draws = [
            d for d in draws if (found := _weekday_for_draw(d)) is not None and found == target_weekday
        ]

    return {"game": game.lower(), "stored": len(draws), "draws": draws}
