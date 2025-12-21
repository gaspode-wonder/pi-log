import os
import tempfile
import responses

from pi_log.storage import (
    initialize_db,
    insert_reading,
    get_unpushed_readings,
    mark_readings_pushed,
)
from pi_log.push_client import PushClient


def create_temp_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    initialize_db(tmp.name)
    return tmp.name


@responses.activate
def test_storage_to_push_to_storage():
    db_path = create_temp_db()

    insert_reading(db_path, {"cps": 9, "cpm": 90, "usv": 0.09, "mode": "FAST"})

    rows = get_unpushed_readings(db_path)

    responses.add(
        responses.POST,
        "http://example.com/api/ingest",
        json={"status": "ok"},
        status=200,
    )

    client = PushClient("http://example.com/api/ingest", "TOKEN")
    pushed_ids = client.push(rows)

    mark_readings_pushed(db_path, pushed_ids)

    remaining = get_unpushed_readings(db_path)

    os.unlink(db_path)

    assert len(remaining) == 0
