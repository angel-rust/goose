"""LinkedIn personal-profile posts via the UGC Posts API.

Needs an OAuth2 access token with the `w_member_social` and `openid` scopes.
The token's owner is resolved through the OpenID userinfo endpoint, so you only
have to supply LINKEDIN_ACCESS_TOKEN. Text-only in this build; image upload
(the register-upload dance) is a clearly scoped future addition.
"""

from __future__ import annotations

import requests

from .. import config
from .base import Platform, PostRequest, PostResult


class LinkedIn(Platform):
    name = "linkedin"
    label = "LinkedIn"
    char_limit = 3000
    supports_local_images = False

    def is_configured(self) -> bool:
        return bool(config.get("LINKEDIN_ACCESS_TOKEN"))

    def missing_credentials(self) -> list[str]:
        return [] if self.is_configured() else ["LINKEDIN_ACCESS_TOKEN"]

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {config.get('LINKEDIN_ACCESS_TOKEN')}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }

    def _author_urn(self) -> str:
        resp = requests.get(
            "https://api.linkedin.com/v2/userinfo", headers=self._headers(), timeout=30
        )
        resp.raise_for_status()
        return f"urn:li:person:{resp.json()['sub']}"

    def publish(self, req: PostRequest) -> PostResult:
        author = self._author_urn()
        payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": req.text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        resp = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"LinkedIn API {resp.status_code}: {resp.text}")
        urn = resp.headers.get("x-restli-id") or resp.json().get("id", "")
        url = f"https://www.linkedin.com/feed/update/{urn}" if urn else None
        return PostResult(platform=self.name, ok=True, id=urn, url=url)
