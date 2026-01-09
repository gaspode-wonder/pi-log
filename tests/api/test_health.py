# no import — pytest fixture "client" is provided automatically


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert "db" in data
    assert data["db"]["status"] in {"ok", "error"}
