from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def setup_state(monkeypatch, tmp_path):
    monkeypatch.setenv("MANUAL_DRAWS_PATH", str(tmp_path / "manual_draws.json"))
    monkeypatch.setenv("TRAINING_STATUS_PATH", str(tmp_path / "training_status.json"))
    monkeypatch.setenv("ADMIN_STATE_PATH", str(tmp_path / "admin_state.json"))


def seed_manual_draw(client: TestClient):
    payload = {
        "game": "EUROMILLION",
        "draws": [
            {"numbers": [1, 2, 3, 4, 5], "stars": [1, 2], "draw_date": "2024-07-12"}
        ],
    }
    assert client.post("/api/admin/manual-draws", json=payload).status_code == 200



def test_admin_console_endpoints(monkeypatch, tmp_path):
    setup_state(monkeypatch, tmp_path)
    client = TestClient(app)
    seed_manual_draw(client)

    stats = client.get("/api/admin/stats")
    assert stats.status_code == 200
    body = stats.json()
    assert body["totalDraws"] == 1
    assert "bytes" in body["dbSize"]

    tables = client.get("/api/admin/db/tables")
    assert tables.status_code == 200
    assert "manual_draws" in tables.json()

    manual_table = client.get("/api/admin/db/table/manual_draws")
    assert manual_table.status_code == 200
    rows = manual_table.json()["rows"]
    assert rows[0]["game"] == "euromillion"

    backup = client.post("/api/admin/db/backup")
    assert backup.status_code == 200
    backup_body = backup.json()["backup"]
    assert backup_body["manual_draws"]["euromillion"]

    assert client.post("/api/admin/db/vacuum").status_code == 200
    assert client.post("/api/admin/db/fix-duplicates").status_code == 200

    # Training modes and history
    assert client.post("/api/admin/train-intense").status_code == 200
    assert client.post("/api/admin/train-targeted").status_code == 200
    history_resp = client.get("/api/admin/ai/history")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) >= 2
    assert {"date", "duration", "model", "score"}.issubset(history[0].keys())

    models = client.get("/api/admin/ai/models")
    assert models.status_code == 200
    model_name = models.json()[0]
    delete_resp = client.post("/api/admin/ai/model/delete", json={"model": model_name})
    assert delete_resp.status_code == 200
    restore_resp = client.post("/api/admin/ai/model/restore", json={"model": model_name})
    assert restore_resp.status_code == 200

    celery_status = client.get("/api/admin/celery-status")
    assert celery_status.status_code == 200
    assert "workers" in celery_status.json()

    assert client.post("/api/admin/restart/backend").status_code == 200
    assert client.post("/api/admin/restart/celery").status_code == 200
    assert client.post("/api/admin/restart/scheduler", json={"schedules": {"trainNightly": True}}).status_code == 200

    logs = client.get("/api/admin/logs")
    assert logs.status_code == 200
    assert "backend" in logs.json()

    assert client.post("/api/admin/logs/clear").status_code == 200
    cleared = client.get("/api/admin/logs")
    assert cleared.status_code == 200

    system_health = client.get("/api/admin/system-health")
    assert system_health.status_code == 200
    assert system_health.json().get("status") is not None

    panic_resp = client.post("/api/admin/panic")
    assert panic_resp.status_code == 200
    assert panic_resp.json()["status"] == "panic"

