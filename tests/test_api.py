from fastapi.testclient import TestClient

from main import GAME_PROFILES, app

client = TestClient(app)


def build_payload(game: str | None = None):
    return {
        "draws": [
            {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2]},
            {"numbers": [2, 3, 4, 5, 6], "stars": [2, 3]},
            {"numbers": [3, 4, 5, 6, 7], "stars": [3, 4]},
        ],
        **({"game": game} if game else {}),
    }


def test_homepage_lists_games_and_disclaimer():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert {game["name"] for game in data.get("games", [])} == {
        "EUROMILLION",
        "EURODREAM",
    }
    disclaimer = data.get("disclaimer", "").lower()
    assert "ludique" in disclaimer
    assert "responsable" in disclaimer
    assert "entertainment" in disclaimer
    assert "responsibly" in disclaimer


def test_frequency_strategy_route_returns_expected_keys():
    response = client.post("/api/generate/frequency", json=build_payload())
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "numbers",
        "stars",
        "confidence_score",
        "method_used",
        "explanation",
        "features",
    }
    assert data["method_used"] == "frequency"
    default_profile = GAME_PROFILES["euromillion"]
    assert len(data["numbers"]) == default_profile["numbers_to_pick"]
    assert len(data["stars"]) == default_profile["stars_to_pick"]


def test_random_strategy_route_returns_sorted_values():
    response = client.post("/api/generate/random", json=build_payload())
    assert response.status_code == 200
    data = response.json()
    assert data["numbers"] == sorted(data["numbers"])
    assert data["stars"] == sorted(data["stars"])


def test_fibo_mcc_spectre_and_meta_ia_routes():
    for strategy in ["fibo", "mcc", "spectre", "meta_ia"]:
        response = client.post(f"/api/generate/{strategy}", json=build_payload())
        assert response.status_code == 200
        data = response.json()
        default_profile = GAME_PROFILES["euromillion"]
        assert len(data["numbers"]) == default_profile["numbers_to_pick"]
        assert len(data["stars"]) == default_profile["stars_to_pick"]
        assert data["method_used"] == strategy


def test_alternate_game_payloads():
    for game in ["eurodream", "EUROMILLION"]:
        response = client.post("/api/generate/random", json=build_payload(game=game))
        assert response.status_code == 200
        data = response.json()
        profile = GAME_PROFILES[game.lower()]
        assert len(data["numbers"]) == profile["numbers_to_pick"]
        assert len(data["stars"]) == profile["stars_to_pick"]


def test_unknown_strategy_returns_404():
    response = client.post("/api/generate/inconnue", json=build_payload())
    assert response.status_code == 404
    assert "Stratégie inconnue" in response.json()["detail"]


def test_empty_history_rejected():
    response = client.post("/api/generate/random", json={"draws": []})
    assert response.status_code == 422
    assert "Historique vide" in response.json()["detail"]


def test_invalid_draw_rejected():
    payload = {"draws": [{"numbers": [1, 1, 2, 3, 4], "stars": [1]}]}
    response = client.post("/api/generate/random", json=payload)
    assert response.status_code == 422
    assert "Tirage invalide" in response.json()["detail"]
