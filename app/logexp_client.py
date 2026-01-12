import requests
import logging


class LogExpClient:
    """
    Minimal client for pushing readings to LogExp.
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.log = logging.getLogger(__name__)

    def push(self, record_id: int, record: dict) -> bool:
        """
        Push a reading to LogExp.

        Returns True on success, False on failure.
        """
        try:
            resp = requests.post(
                f"{self.base_url}/api/readings",
                json={"id": record_id, **record},
                headers={"X-API-Key": self.token},
                timeout=5,
            )
            resp.raise_for_status()
            return True

        except Exception as exc:
            self.log.error(f"LogExp push failed: {exc}")
            return False
