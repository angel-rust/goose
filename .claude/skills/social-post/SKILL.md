---
name: social-post
description: Draft, adapt, and cross-post content to social media (X, Bluesky, Mastodon, LinkedIn, Threads) via the social-media-agent MCP server. Use whenever the user wants to post, tweet, share, announce, or cross-post something to their social accounts.
---

# Social Post

Turn a single idea into platform-native posts and publish them everywhere the
user has configured — fast, with one confirmation gate before anything goes live.

## Tools (from the `social-media-agent` MCP server)

- `list_platforms` — which networks are configured + their char limits.
- `preview` — dry-run; returns char counts and warnings, posts nothing.
- `post(text, platforms, image_paths)` — publishes. `platforms` is `"all"`, a
  name (`"bluesky"`), or a list. Returns per-platform result URLs.

## Workflow

1. **Check what's live.** Call `list_platforms`. Only configured platforms can
   receive posts. If none are configured, point the user to
   `social-media-agent/.env.example` and stop.

2. **Get the core message.** If the user gave content, use it. If they gave a
   rough idea, draft from it. Confirm the angle before expanding.

3. **Adapt per platform** — do NOT post identical text everywhere. Tailor:
   - **X / Twitter** (280): tight, punchy, 1–2 hashtags max, hook first.
   - **Bluesky** (300): conversational, link-friendly, light on hashtags.
   - **Mastodon** (500): can be longer, CW-friendly, hashtags help discovery.
   - **LinkedIn** (3000): professional framing, line breaks, a takeaway/CTA.
   - **Threads** (500): casual, native phrasing, sparse hashtags.

   Group platforms that can share identical copy; tailor the rest individually.

4. **Preview before sending.** Show the user the final per-platform drafts in a
   readable block. Call `preview` to catch any over-limit copy and fix it.

5. **Confirm.** Always get an explicit go-ahead before publishing. Publishing is
   public and hard to undo. Never post without confirmation.

6. **Publish.** Call `post` per copy-group:
   - Same copy for several platforms → one call: `post(text, ["x","bluesky"])`.
   - Tailored copy → one call each: `post(tailored, "linkedin")`.
   Attach `image_paths` only for X/Bluesky/Mastodon (others ignore local images).

7. **Report.** Summarize results with the returned URLs. Call out any platform
   that failed or was skipped, and why.

## Guardrails

- One confirmation gate, every time — even if the user said "post it" earlier in
  a long thread, confirm the final drafts.
- Respect char limits; never silently truncate — rewrite to fit and show the user.
- If a platform errors, report it plainly and keep the successful posts; don't
  retry blindly or repost to platforms that already succeeded.
- Never invent engagement claims or hashtags the user didn't approve.
