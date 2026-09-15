---
name: website-clone
description: "Clone or mimic a site's look as a one-file HTML replica."
---

# Clone a website's visual style

Goal: produce a faithful single-file `index.html` replica of a target site, using the site's *real* content and *real* assets, matched to its actual visual style.

## When to use
- "сделай копию этого сайта", "clone this site", "recreate this aesthetic", "make it look like X".
- Building a portfolio/landing/art-site clone for reference or as a starting template.

## Workflow
1. **Fetch the real source.** `curl -sL <url> -o page.html`. Also pull linked CSS (look for `/_astro/*.css` or `/assets/*.css` in the HTML). Extract design tokens (colors, fonts, radii) from `:root` vars and key class rules.
2. **Extract embedded data.** Many modern sites (Astro, Next, etc.) render client-side from JSON in the HTML. See `references/extraction.md` for the Astro `<astro-island props="...">` unwrap pattern and the headless-screenshot command.
3. **Capture a REAL rendered screenshot** of the target — do NOT guess the style from text alone. The browser tool is often blocked (see Pitfalls); use the headless-Chrome recipe in `references/extraction.md`.
4. **Read the design with vision_analyze** on that screenshot: background, icon grid, window chrome, typography, dock/ticker, accent colors, default-open windows. Note what is *real* vs what you assumed.
5. **Build the clone** as one self-contained `index.html` (inline CSS + JS, real CDN image URLs). Use real fonts via Google Fonts. Match the confirmed style, not your first guess.
6. **Verify by screenshot-comparison**: serve it (`python3 -m http.server`), headless-screenshot it, vision_analyze side-by-side with the original, and iterate on the gaps.

## Pitfalls
- **`browser_exec` (the in-app browser tool) is frequently blocked** by a "Allow remote debugging?" popup in Chrome that the user must click per-connection. It will keep failing until they click Allow. Don't burn turns on it — fall back to the **headless Chrome `--screenshot`** recipe in `references/extraction.md` (a real Chrome binary, not the harness one).
- **Headless Chrome hangs on its background updater** even after the screenshot PNG is written (`exit 124`/never returns). Fix: run it `background=true`, then in a *separate* terminal call `ls -la /tmp/out.png` to confirm the file exists, then `process(action='kill')`. Never wait synchronously on it.
- **Don't use a `__DATA__` placeholder + separate replace step** when writing a single file — the replacement can fail to persist (the read/write race in execute_code silently reverts). Bake the JSON/values directly into the `write_file` content.
- **JSON-in-script gotcha:** never embed a JSON payload in `<script id="data" type="application/json">` that contains the literal string `</script>`; it will truncate the DOM. (Astro's `props="..."` is an HTML attribute, not a script, so it's safe — extract it with regex + `json.loads`.)
- **CDP / chrome-devtools-mcp on port 9222 can hit the WRONG Chrome.** Two Chrome processes can share `:9222` — the user's *personal* Chrome (binds IPv4 `127.0.0.1`, returns `404` to `/json`) and a debuggable one (binds IPv6 `[::1]`). A MCP server pointed at `http://127.0.0.1:9222` will connect to the personal Chrome and fail. Point it at `http://localhost:9222` or `http://[::1]:9222` instead. (Direct `curl http://[::1]:9222/json/version` works; the `websocket-client` WS upgrade may still fail — prefer the `--screenshot`/`--dump-dom` binary route.)
- **Client-rendered shells:** if `<body>` is nearly empty (just `<astro-island>` / `<div id="root">`), the whole UI is built from embedded JSON props. Extract and unwrap that JSON (recipe in references) — the visible content is NOT in the static HTML.

## Verification
- Serve (`python3 -m http.server 8911`) and headless-screenshot the clone; `vision_analyze` comparing original vs clone; check every JS-generated element actually rendered (grep the `--dump-dom` output for generated class names like `class="icon"`).
- Confirm linked assets return `200` (`curl -o /dev/null -w "%{http_code}" <asset>`).
