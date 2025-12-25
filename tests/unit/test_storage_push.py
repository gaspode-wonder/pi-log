import responses

from app.sqlite_store import SQLiteStore
from app.api_client import APIClient


@responses.activate
def test_storage_to_push_to_storage(fake_store):
    store = fake_store

    # Insert a reading
    reading_id = store.insert_record({"cps": 9, "cpm": 90, "usv": 0.09, "mode": "FAST"})

    # Mock push endpoint
    responses.add(
        responses.POST,
        "http://example.com/api/readings",
        json={"status": "ok"},
        status=200,
    )

    client = APIClient("http://example.com/api", "TOKEN")

    # Push unpushed readings
    unpushed = store.select_unpushed_readings()
    for r in unpushed:
        client.push_record(r["id"], r)
        store.mark_readings_pushed([r["id"]])

    # Ensure reading is no longer unpushed
    remaining = store.select_unpushed_readings()
    assert all(r["id"] != reading_id for r in remaining)
