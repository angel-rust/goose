"""Mastodon via the REST API.

One access token from your instance (Preferences -> Development -> New
Application, scope `write:statuses` and `write:media`). Works with any
instance; set MASTODON_INSTANCE to your server's base URL.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path

import requests

from .. import config
from .base import Platform, PostRequest, PostResult


class Mastodon(Platform):
    name = "mastodon"
    label = "Mastodon"
    char_limit = 500
    supports_local_images = True

    def _instance(self) -> str | None:
        instance = config.get("MASTODON_INSTANCE")
        return instance.rstrip("/") if instance else None

    def is_configured(self) -> bool:
        return bool(self._instance() and config.get("MASTODON_ACCESS_TOKEN"))

    def missing_credentials(self) -> list[str]:
        missing = []
        if not self._instance():
            missing.append("MASTODON_INSTANCE")
        if not config.get("MASTODON_ACCESS_TOKEN"):
            missing.append("MASTODON_ACCESS_TOKEN")
        return missing

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {config.get('MASTODON_ACCESS_TOKEN')}"}

    def _upload_images(self, image_paths: list[str]) -> list[str]:
        ids = []
        for path in image_paths[:4]:
            mime = mimetypes.guess_type(path)[0] or "image/jpeg"
            with open(path, "rb") as fh:
                resp = requests.post(
                    f"{self._instance()}/api/v2/media",
                    headers=self._headers(),
                    files={"file": (Path(path).name, fh, mime)},
                    timeout=120,
                )
            resp.raise_for_status()
            ids.append(resp.json()["id"])
        return ids

    def publish(self, req: PostRequest) -> PostResult:
        payload: dict = {"status": req.text}
        if req.image_paths:
            payload["media_ids[]"] = self._upload_images(req.image_paths)

        resp = requests.post(
            f"{self._instance()}/api/v1/statuses",
            headers=self._headers(),
            data=payload,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        return PostResult(
            platform=self.name, ok=True, id=str(body.get("id")), url=body.get("url")
        )
