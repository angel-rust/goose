"""Bluesky via the AT Protocol XRPC endpoints (no SDK dependency).

Auth is an app password (Settings -> App Passwords on bsky.app), not your real
password. Two calls: open a session, then create the post record. Images are
uploaded as blobs and embedded.
"""

from __future__ import annotations

import mimetypes
from datetime import datetime, timezone
from pathlib import Path

import requests

from .. import config
from .base import Platform, PostRequest, PostResult

PDS = "https://bsky.social"


class Bluesky(Platform):
    name = "bluesky"
    label = "Bluesky"
    char_limit = 300
    supports_local_images = True

    def _creds(self) -> tuple[str | None, str | None]:
        return config.get("BLUESKY_HANDLE"), config.get("BLUESKY_APP_PASSWORD")

    def is_configured(self) -> bool:
        return all(self._creds())

    def missing_credentials(self) -> list[str]:
        handle, pw = self._creds()
        missing = []
        if not handle:
            missing.append("BLUESKY_HANDLE")
        if not pw:
            missing.append("BLUESKY_APP_PASSWORD")
        return missing

    def _session(self) -> dict:
        handle, password = self._creds()
        resp = requests.post(
            f"{PDS}/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": password},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def _upload_images(self, jwt: str, image_paths: list[str]) -> list[dict]:
        images = []
        for path in image_paths[:4]:
            data = Path(path).read_bytes()
            mime = mimetypes.guess_type(path)[0] or "image/jpeg"
            resp = requests.post(
                f"{PDS}/xrpc/com.atproto.repo.uploadBlob",
                headers={"Authorization": f"Bearer {jwt}", "Content-Type": mime},
                data=data,
                timeout=60,
            )
            resp.raise_for_status()
            images.append({"alt": "", "image": resp.json()["blob"]})
        return images

    def publish(self, req: PostRequest) -> PostResult:
        session = self._session()
        jwt, did = session["accessJwt"], session["did"]

        record: dict = {
            "$type": "app.bsky.feed.post",
            "text": req.text,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        if req.image_paths:
            record["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": self._upload_images(jwt, req.image_paths),
            }

        resp = requests.post(
            f"{PDS}/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {jwt}"},
            json={"repo": did, "collection": "app.bsky.feed.post", "record": record},
            timeout=30,
        )
        resp.raise_for_status()
        uri = resp.json()["uri"]
        rkey = uri.rsplit("/", 1)[-1]
        handle = config.get("BLUESKY_HANDLE")
        return PostResult(
            platform=self.name,
            ok=True,
            id=uri,
            url=f"https://bsky.app/profile/{handle}/post/{rkey}",
        )
