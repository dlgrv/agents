---
name: web-research-fallbacks
description: Use when search fails or a site 403s the browser.
version: 1.0.0
author: dlgrv
license: MIT
metadata:
  hermes:
    tags: [web, browser, research, anti-bot]
    related_skills: [grounded-citations]
category: research
---

# Web research fallbacks

## When to Use

Falls back from broken search to the page text. Trigger cases: results in the wrong locale (German/Dutch pages for a Russian query), results answering a homophone of the keyword, empty results for a `site:` query that must exist, 403 'Forbidden / Guru meditation' (Qrator anti-bot) on the target site, or a captcha wall on Yandex/DDG.

## Ladder (in order, stop when you have the text)

1. **Detect backend failure early.** After 2 failed query reformulations, stop rephrasing — the backend is ignoring the query; switch to direct navigation.
2. **Go direct via browser.** `new_tab("https://<known-url>")` and read `document.body.innerText` via `js()`. Guess plausible paths from the site's footer/nav names before searching for them.
3. **On 403 'Forbidden / Guru meditation':** the page is fine, the browser's egress IP is blocked. Retrying the URL, waiting, or opening a new tab will not help. Route through a reader proxy: `goto_url("https://r.jina.ai/<original-url>")`, then sleep 10–15 s and read the body — it returns the page as markdown with links intact.
4. **On captcha walls (Yandex SmartCaptcha, DuckDuckGo bot-check):** dead end — never attempt to solve or click through. Fall back to step 3 for the target page directly.

## Pitfalls

- `goto_url` may raise `Page.navigate timed out after 5s` **while navigation actually succeeds**. Wrap it in try/except, sleep 10–15 s, then check `page_info()` / body text before declaring failure. Never conclude a page is unreachable from this error alone.
- Reader-proxy responses are cached by URL: a second fetch can return a shorter/older snapshot. Read whatever arrived fully (`len` first) before deciding the page is truncated.
- Keyword homophones are a trap for RU retail/tech queries (site names like DNS/ДНС collide with networking terms). Prefer exact site URLs and on-site navigation over general web search for such targets.
