import requests
from app.logging_loader import get_logger
log = get_logger(__name__)


class APIClient:
    """
    Simple HTTP client for pushing readings to a remote API.
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def push_record(self, record_id: int, reading: dict):
        """
        Push a single reading to the remote API.
        """
        url = f"{self.base_url}/readings"
        headers = {"Authorization": f"Bearer {self.token}"}

        payload = {
            "id": record_id,
            "timestamp": reading.get("timestamp"),
            "cps": reading.get("cps"),
            "cpm": reading.get("cpm"),
            "usv": reading.get("usv"),
            "mode": reading.get("mode"),
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            resp.raise_for_status()
            log.info(f"Pushed reading {record_id} to API")
        except Exception as exc:
            log.error(f"Failed to push reading {record_id}: {exc}")
