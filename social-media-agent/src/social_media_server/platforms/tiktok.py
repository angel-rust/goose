"""TikTok stub.

TikTok's Content Posting API is video-only and gated behind app review plus a
per-user OAuth flow. There is no text-post equivalent, so this stays a stub
until you have an approved app. The scaffolding (env vars, registration) is in
place so wiring it up later is a single file change.

To enable: get a TikTok developer app approved for content.posting scope, run
the OAuth flow to obtain a user access token, then implement `publish` against
the /v2/post/publish/video/init/ endpoint (init -> upload -> status poll).
"""

from __future__ import annotations

from .. import config
from .base import Platform, PostRequest, PostResult


class TikTok(Platform):
    name = "tiktok"
    label = "TikTok"
    char_limit = 2200  # video caption limit
    supports_local_images = False

    def is_configured(self) -> bool:
        # Intentionally False until the video-publishing flow is implemented.
        return False

    def missing_credentials(self) -> list[str]:
        return ["TIKTOK_ACCESS_TOKEN (video-publish flow not yet implemented)"]

    def publish(self, req: PostRequest) -> PostResult:
        return PostResult(
            platform=self.name,
            ok=False,
            error=(
                "TikTok publishing is not implemented: it is video-only and requires "
                "an approved developer app. See platforms/tiktok.py for the wiring steps."
            ),
        )
