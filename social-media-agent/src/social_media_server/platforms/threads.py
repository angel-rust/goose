"""Threads via the official Meta Threads API.

Two-step publish: create a media container, then publish it. Needs a long-lived
access token and your Threads user id (from the Threads API setup in the Meta
developer dashboard). Images must be reachable at a public URL — Threads pulls
them server-side — so local image files are not supported here.
"""

from __future__ import annotations

import requests

from .. import config
from .base import Platform, PostRequest, PostResult

BASE = "https://graph.threads.net/v1.0"


class Threads(Platform):
    name = "threads"
    label = "Threads"
    char_limit = 500
    supports_local_images = False

    def _creds(self) -> tuple[str | None, str | None]:
        return config.get("THREADS_USER_ID"), config.get("THREADS_ACCESS_TOKEN")

    def is_configured(self) -> bool:
        return all(self._creds())

    def missing_credentials(self) -> list[str]:
        user_id, token = self._creds()
        missing = []
        if not user_id:
            missing.append("THREADS_USER_ID")
        if not token:
            missing.append("THREADS_ACCESS_TOKEN")
        return missing

    def publish(self, req: PostRequest) -> PostResult:
        user_id, token = self._creds()

        create = requests.post(
            f"{BASE}/{user_id}/threads",
            params={"media_type": "TEXT", "text": req.text, "access_token": token},
            timeout=30,
        )
        if create.status_code >= 400:
            raise RuntimeError(f"Threads create {create.status_code}: {create.text}")
        creation_id = create.json()["id"]

        publish = requests.post(
            f"{BASE}/{user_id}/threads_publish",
            params={"creation_id": creation_id, "access_token": token},
            timeout=30,
        )
        if publish.status_code >= 400:
            raise RuntimeError(f"Threads publish {publish.status_code}: {publish.text}")
        media_id = publish.json()["id"]
        return PostResult(platform=self.name, ok=True, id=media_id)
