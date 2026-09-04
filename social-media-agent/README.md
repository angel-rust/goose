# Social Media Agent

An MCP server + Claude Code skill that turns one idea into platform-native posts
and cross-posts them to all your accounts. Built so the agent does the writing
and you hit confirm.

| Platform | Status | Auth | Local images |
|----------|--------|------|--------------|
| X / Twitter | ✅ implemented | OAuth 1.0a (4 keys) | yes |
| Bluesky | ✅ implemented | app password | yes |
| Mastodon | ✅ implemented | access token | yes |
| LinkedIn | ✅ implemented | OAuth2 token | not yet (text) |
| Threads | ✅ implemented | long-lived token + user id | URL only |
| TikTok | 🚧 stub | — | video-only, needs app approval |

## Architecture

```
social-media-agent/
  src/social_media_server/
    server.py              # MCP tools: list_platforms, preview, post
    config.py              # loads .env, no override of real env vars
    platforms/
      base.py              # Platform contract (subclass to add a network)
      bluesky.py mastodon.py twitter.py linkedin.py threads.py tiktok.py
      __init__.py          # ALL_PLATFORMS registry — single source of truth
```

Adding a network = one new file implementing `Platform.publish` + one line in
`platforms/__init__.py`. The server discovers it; the skill uses it.

## Setup

1. **Install deps** (uses [uv](https://docs.astral.sh/uv/)):
   ```bash
   cd social-media-agent
   uv sync          # or: pip install -r requirements.txt
   ```

2. **Add credentials**:
   ```bash
   cp .env.example .env
   # fill in ONLY the platforms you want — the server auto-detects the rest
   ```
   Fastest first win: **Bluesky** (Settings → App Passwords, no approval needed).

3. **Register with Claude Code** — already done via `../.mcp.json` at the repo
   root. Restart Claude Code and the `social-media-agent` server loads. Verify:
   ```bash
   uv run --directory social-media-agent python -m social_media_server   # starts the MCP server (stdio)
   ```

## Usage

Just talk to Claude Code. The `social-post` skill (in `.claude/skills/`) kicks
in automatically:

> "Post that we just shipped v2 of the API — make it land well on each network."

Claude will: check configured platforms → draft platform-native copy → preview
char counts → **ask you to confirm** → publish → hand back the post URLs.

Or drive the tools directly:
- `list_platforms` — see what's configured
- `preview` — dry-run, no posting
- `post(text, platforms, image_paths)` — publish

## Getting credentials

- **Bluesky**: bsky.app → Settings → App Passwords. Set `BLUESKY_HANDLE` +
  `BLUESKY_APP_PASSWORD`.
- **Mastodon**: your instance → Preferences → Development → New application
  (scopes `write:statuses write:media`). Set `MASTODON_INSTANCE` +
  `MASTODON_ACCESS_TOKEN`.
- **X / Twitter**: developer.twitter.com → Project + App with Read+Write →
  Keys and tokens. Set the four `TWITTER_*` values.
- **LinkedIn**: OAuth2 app with `openid w_member_social` scopes →
  `LINKEDIN_ACCESS_TOKEN`.
- **Threads**: Meta developer dashboard → Threads API → long-lived token +
  `THREADS_USER_ID`.

## Security

- `.env` is gitignored — credentials never get committed. Keep it that way.
- Tokens grant posting rights to your accounts; treat them like passwords.
- The skill enforces a confirmation gate before anything publishes.

## Roadmap

- LinkedIn / Threads image upload (register-upload flow)
- Bluesky rich-text facets (clickable links & mentions)
- X thread support (chained replies)
- TikTok video publishing once an app is approved
