import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_manual_draw_import_and_listing(monkeypatch, tmp_path):
    manual_store = tmp_path / "manual_draws.json"
    monkeypatch.setenv("MANUAL_DRAWS_PATH", str(manual_store))

    client = TestClient(app)
    payload = {
        "game": "EUROMILLION",
        "draws": [
            {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2]},
            {"numbers": [6, 7, 8, 9, 10], "stars": [3, 4]},
        ],
    }

    response = client.post("/api/admin/manual-draws", json=payload)
    assert response.status_code == 200
    assert response.json() == {"game": "euromillion", "stored": 2}

    # Verify persistence on disk
    saved_content = json.loads(Path(manual_store).read_text(encoding="utf-8"))
    assert "euromillion" in saved_content
    assert len(saved_content["euromillion"]) == 2

    # Listing reflects the stored draws
    listing = client.get("/api/admin/manual-draws/euromillion")
    assert listing.status_code == 200
    listing_data = listing.json()
    assert listing_data["stored"] == 2
    assert listing_data["draws"][0]["numbers"] == [1, 2, 3, 4, 5]


def test_manual_draw_import_rejects_invalid_game(monkeypatch, tmp_path):
    monkeypatch.setenv("MANUAL_DRAWS_PATH", str(tmp_path / "manual_draws.json"))
    client = TestClient(app)
    payload = {"game": "unknown", "draws": [{"numbers": [1, 2, 3, 4, 5], "stars": [1, 2]}]}

    response = client.post("/api/admin/manual-draws", json=payload)
    assert response.status_code == 422
    assert "Jeu inconnu" in response.json()["detail"]
