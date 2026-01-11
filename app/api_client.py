# filename: app/api_client.py

from __future__ import annotations

import json
from typing import List, Optional

import requests

from app.models import GeigerRecord


class PushClient:
    """
    Responsible for pushing canonical ingestion payloads to LogExp.

    This client:
        - Accepts GeigerRecord objects
        - Converts them to canonical ingestion payloads
        - Sends them to LogExp's ingestion endpoint
        - Returns the list of successfully pushed record IDs

    Local-only fields (raw, timestamp, pushed, id) are NOT sent.

    NOTE:
        api_url and api_token may be Optional at the type level,
        but this client will raise if constructed without both.
        geiger_reader.py ensures this never happens in practice.
    """

    def __init__(self, api_url: Optional[str], api_token: Optional[str]):
        if api_url is None or api_token is None:
            raise ValueError("PushClient requires both api_url and api_token")

        # Safe to use as str from here on
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token

        # The ingestion endpoint is always /api/readings/ingest
        self.ingest_url = f"{self.api_url}/api/readings/ingest"

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

    def push(self, records: List[GeigerRecord]) -> List[int]:
        """
        Push a batch of GeigerRecord objects to LogExp.

        Returns:
            List of record IDs that were successfully pushed.
        """
        if not records:
            return []

        payload = [rec.to_logexp_payload() for rec in records]

        try:
            resp = requests.post(
                self.ingest_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=5,
            )
        except Exception:
            # Network or connection failure — nothing was pushed
            return []

        if resp.status_code != 200:
            # LogExp rejected the batch — nothing was pushed
            return []

        try:
            data = resp.json()
        except Exception:
            return []

        # LogExp returns: { "pushed_ids": [1, 2, 3] }
        pushed_ids = data.get("pushed_ids", [])
        if not isinstance(pushed_ids, list):
            return []

        # Map pushed IDs back to local DB IDs
        local_ids: List[int] = []
        for rec in records:
            if rec.id is not None and rec.id in pushed_ids:
                local_ids.append(rec.id)

        return local_ids
