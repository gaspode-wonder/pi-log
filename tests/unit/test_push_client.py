import json
import responses
from pi_log.push_client import PushClient


@responses.activate
def test_push_success_marks_rows():
    client = PushClient("http://example.com/api/ingest", "TOKEN")

    responses.add(
        responses.POST,
        "http://example.com/api/ingest",
        json={"status": "ok"},
        status=200,
    )

    rows = [
        {"id": 1, "cps": 10, "cpm": 100, "usv": 0.10, "mode": "SLOW"},
        {"id": 2, "cps": 20, "cpm": 200, "usv": 0.20, "mode": "FAST"},
    ]

    pushed = client.push(rows)

    assert pushed == [1, 2]


@responses.activate
def test_push_failure_returns_empty_list():
    client = PushClient("http://example.com/api/ingest", "TOKEN")

    responses.add(
        responses.POST,
        "http://example.com/api/ingest",
        status=500,
    )

    rows = [{"id": 1, "cps": 10, "cpm": 100, "usv": 0.10, "mode": "SLOW"}]

    pushed = client.push(rows)

    assert pushed == []


@responses.activate
def test_payload_structure():
    client = PushClient("http://example.com/api/ingest", "TOKEN")

    responses.add(
        responses.POST,
        "http://example.com/api/ingest",
        json={"status": "ok"},
        status=200,
    )

    rows = [{"id": 1, "cps": 5, "cpm": 50, "usv": 0.05, "mode": "INST"}]

    client.push(rows)

    sent = json.loads(responses.calls[0].request.body)

    assert "readings" in sent
    assert sent["readings"][0]["cps"] == 5
    assert sent["readings"][0]["mode"] == "INST"
