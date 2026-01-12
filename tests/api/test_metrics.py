# no import — pytest fixture "client" is provided automatically


def test_metrics_shape(client):
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    assert "ingested_count" in data
    assert "uptime_seconds" in data
    assert "version" in data
