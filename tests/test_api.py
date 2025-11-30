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


def test_unknown_game_returns_422():
    payload = build_payload(game="eurobillion")
    response = client.post("/api/generate/random", json=payload)
    assert response.status_code == 422
    assert "Jeu inconnu" in response.json()["detail"]


def test_empty_history_rejected():
    response = client.post("/api/generate/random", json={"draws": []})
    assert response.status_code == 422
    assert "Historique vide" in response.json()["detail"]


def test_invalid_draw_rejected():
    payload = {"draws": [{"numbers": [1, 1, 2, 3, 4], "stars": [1]}]}
    response = client.post("/api/generate/random", json=payload)
    assert response.status_code == 422
    assert "Tirage invalide" in response.json()["detail"]


def test_generate_can_use_manual_store(monkeypatch, tmp_path):
    manual_store = tmp_path / "manual_draws.json"
    monkeypatch.setenv("MANUAL_DRAWS_PATH", str(manual_store))
    local_client = TestClient(app)

    # Ingestion manuelle préalable
    ingest_payload = {
        "game": "eurodream",
        "draws": [
            {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2], "draw_date": "2024-06-18"},
            {"numbers": [6, 7, 8, 9, 10], "stars": [3, 4], "draw_date": "2024-06-21"},
        ],
    }
    ingest = local_client.post("/api/admin/manual-draws", json=ingest_payload)
    assert ingest.status_code == 200

    # Génération en s'appuyant uniquement sur le store manuel
    response = local_client.post(
        "/api/generate/random",
        json={"draws": [], "game": "eurodream", "use_manual_draws": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["numbers"]) == GAME_PROFILES["eurodream"]["numbers_to_pick"]
    assert len(data["stars"]) == GAME_PROFILES["eurodream"]["stars_to_pick"]


def test_generate_rejects_manual_flag_without_history(monkeypatch, tmp_path):
    monkeypatch.setenv("MANUAL_DRAWS_PATH", str(tmp_path / "manual_draws.json"))
    local_client = TestClient(app)

    response = local_client.post(
        "/api/generate/random",
        json={"draws": [], "game": "euromillion", "use_manual_draws": True},
    )
    assert response.status_code == 404
    assert "Aucun tirage manuel" in response.json()["detail"]


def test_health_exposes_games_and_strategies():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert set(data["games"]) == {"euromillion", "eurodream"}
    assert {"frequency", "random", "fibo", "mcc", "spectre", "meta_ia"}.issubset(
        set(data["strategies"])
    )
