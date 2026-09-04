"""MCP server exposing social posting tools.

Tools:
  - list_platforms : which networks are wired up and configured
  - preview        : dry-run that surfaces per-platform warnings (no posting)
  - post           : publish text (+ optional local images) to one/many/all networks

Designed so the agent's job is to craft good copy and pick targets; this server
handles auth and the platform-specific API quirks.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from . import config
from .platforms import ALL_PLATFORMS, BY_NAME, PostRequest

config.load_env()

mcp = FastMCP("social-media-agent")


def _resolve_targets(platforms: str | list[str]) -> list:
    if platforms in ("all", ["all"]):
        return [p for p in ALL_PLATFORMS if p.is_configured()]
    names = [platforms] if isinstance(platforms, str) else platforms
    resolved = []
    for name in names:
        platform = BY_NAME.get(name.strip().lower())
        if platform:
            resolved.append(platform)
    return resolved


@mcp.tool()
def list_platforms() -> str:
    """List every supported network, whether it is configured, and its limits.

    Call this first so you know which targets are available before drafting.
    """
    rows = []
    for p in ALL_PLATFORMS:
        rows.append(
            {
                "name": p.name,
                "label": p.label,
                "configured": p.is_configured(),
                "char_limit": p.char_limit,
                "supports_local_images": p.supports_local_images,
                "missing_credentials": p.missing_credentials(),
            }
        )
    return json.dumps(rows, indent=2)


@mcp.tool()
def preview(text: str, platforms: str | list[str] = "all") -> str:
    """Dry-run a post: report char counts and per-platform warnings without sending.

    Use this to catch over-limit copy before publishing. `platforms` is "all", a
    single platform name, or a list of names.
    """
    targets = _resolve_targets(platforms)
    if not targets:
        return "No configured platforms match that selection. Run list_platforms."
    req = PostRequest(text=text)
    out = []
    for p in targets:
        out.append(
            {
                "platform": p.name,
                "chars": len(text),
                "char_limit": p.char_limit,
                "warning": p.validate(req),
            }
        )
    return json.dumps(out, indent=2)


@mcp.tool()
def post(
    text: str,
    platforms: str | list[str] = "all",
    image_paths: list[str] | None = None,
) -> str:
    """Publish `text` to the chosen networks. Returns per-platform results with URLs.

    Args:
        text: The post body. Keep it within each target's char limit (see preview).
        platforms: "all" (every configured network), a single name like "bluesky",
            or a list like ["twitter", "bluesky"]. Valid names: twitter, bluesky,
            mastodon, linkedin, threads, tiktok.
        image_paths: Optional local image file paths. Only attached on networks that
            support local images (twitter, bluesky, mastodon); ignored elsewhere.
    """
    targets = _resolve_targets(platforms)
    if not targets:
        return json.dumps(
            {"error": "No configured platforms match that selection. Run list_platforms."}
        )

    req = PostRequest(text=text, image_paths=image_paths or [])
    results = []
    for p in targets:
        if not p.is_configured():
            results.append(
                {
                    "platform": p.name,
                    "ok": False,
                    "skipped": True,
                    "error": f"not configured; set {p.missing_credentials()}",
                }
            )
            continue
        try:
            result = p.publish(req)
            results.append(
                {
                    "platform": result.platform,
                    "ok": result.ok,
                    "url": result.url,
                    "id": result.id,
                    "error": result.error,
                }
            )
        except Exception as exc:  # surface, don't crash the whole cross-post
            results.append({"platform": p.name, "ok": False, "error": str(exc)})
    return json.dumps(results, indent=2)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
