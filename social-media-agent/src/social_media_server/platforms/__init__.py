"""Platform registry.

`ALL_PLATFORMS` is the single source of truth. Add a new network by importing
its class and appending an instance here.
"""

from __future__ import annotations

from .base import Platform, PostRequest, PostResult
from .bluesky import Bluesky
from .linkedin import LinkedIn
from .mastodon import Mastodon
from .threads import Threads
from .tiktok import TikTok
from .twitter import Twitter

ALL_PLATFORMS: list[Platform] = [
    Twitter(),
    Bluesky(),
    Mastodon(),
    LinkedIn(),
    Threads(),
    TikTok(),
]

BY_NAME: dict[str, Platform] = {p.name: p for p in ALL_PLATFORMS}

__all__ = ["ALL_PLATFORMS", "BY_NAME", "Platform", "PostRequest", "PostResult"]
