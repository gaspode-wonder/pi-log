import requests

class PushClient:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    def push(self, rows):
        if not rows:
            return []

        # Normalize sqlite3.Row → dict
        normalized = []
        for row in rows:
            if isinstance(row, dict):
                normalized.append(row)
            else:
                normalized.append(dict(row))

        payload = {"readings": normalized}

        try:
            resp = requests.post(
                self.url,
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=5,
            )
        except requests.RequestException:
            return []

        if resp.status_code != 200:
            return []

        return [row["id"] for row in normalized]
