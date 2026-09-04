"""Platform plugin contract.

Every social network is a subclass of `Platform`. To add a network, drop a new
file in this package, implement `post`, and register it in `ALL_PLATFORMS`
(platforms/__init__.py). The server discovers it automatically.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class PostResult:
    platform: str
    ok: bool
    url: str | None = None
    id: str | None = None
    error: str | None = None
    skipped: bool = False


@dataclass
class PostRequest:
    text: str
    image_paths: list[str] = field(default_factory=list)


class Platform(ABC):
    """A social network the agent can publish to."""

    #: Stable identifier used in tool arguments, e.g. "bluesky".
    name: str = ""
    #: Human-facing label, e.g. "Bluesky".
    label: str = ""
    #: Maximum characters per post, or None if effectively unlimited.
    char_limit: int | None = None
    #: Whether this platform can attach local images in the current build.
    supports_local_images: bool = False

    @abstractmethod
    def is_configured(self) -> bool:
        """True when all required credentials are present in the environment."""

    @abstractmethod
    def missing_credentials(self) -> list[str]:
        """Names of env vars that must be set for this platform to work."""

    @abstractmethod
    def publish(self, req: PostRequest) -> PostResult:
        """Publish a post. Raises on hard failure; returns a PostResult on success."""

    def validate(self, req: PostRequest) -> str | None:
        """Return a human-readable warning if the request looks problematic."""
        if self.char_limit is not None and len(req.text) > self.char_limit:
            return (
                f"{self.label}: text is {len(req.text)} chars, over the "
                f"{self.char_limit} limit by {len(req.text) - self.char_limit}."
            )
        if req.image_paths and not self.supports_local_images:
            return f"{self.label}: image upload is not supported yet; posting text only."
        return None
