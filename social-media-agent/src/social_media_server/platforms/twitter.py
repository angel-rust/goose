"""X / Twitter via API v2 with OAuth 1.0a user-context auth.

You need a project + app in the X developer portal with Read+Write permission,
then four values: API key/secret (consumer) and an access token/secret for your
account. Posting a tweet is the free tier's main allowance. Images are uploaded
through the v1.1 media endpoint and attached to the v2 tweet.
"""

from __future__ import annotations

from requests_oauthlib import OAuth1Session

from .. import config
from .base import Platform, PostRequest, PostResult

_REQUIRED = [
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_SECRET",
]


class Twitter(Platform):
    name = "twitter"
    label = "X / Twitter"
    char_limit = 280
    supports_local_images = True

    def is_configured(self) -> bool:
        return all(config.get(k) for k in _REQUIRED)

    def missing_credentials(self) -> list[str]:
        return [k for k in _REQUIRED if not config.get(k)]

    def _session(self) -> OAuth1Session:
        return OAuth1Session(
            config.get("TWITTER_API_KEY"),
            client_secret=config.get("TWITTER_API_SECRET"),
            resource_owner_key=config.get("TWITTER_ACCESS_TOKEN"),
            resource_owner_secret=config.get("TWITTER_ACCESS_SECRET"),
        )

    def _upload_images(self, oauth: OAuth1Session, image_paths: list[str]) -> list[str]:
        ids = []
        for path in image_paths[:4]:
            with open(path, "rb") as fh:
                resp = oauth.post(
                    "https://upload.twitter.com/1.1/media/upload.json",
                    files={"media": fh},
                    timeout=120,
                )
            resp.raise_for_status()
            ids.append(resp.json()["media_id_string"])
        return ids

    def publish(self, req: PostRequest) -> PostResult:
        oauth = self._session()
        payload: dict = {"text": req.text}
        if req.image_paths:
            payload["media"] = {"media_ids": self._upload_images(oauth, req.image_paths)}

        resp = oauth.post(
            "https://api.twitter.com/2/tweets", json=payload, timeout=30
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"X API {resp.status_code}: {resp.text}")
        tweet_id = resp.json()["data"]["id"]
        return PostResult(
            platform=self.name,
            ok=True,
            id=tweet_id,
            url=f"https://twitter.com/i/web/status/{tweet_id}",
        )
