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
2. **Go direct via terminal curl (works with no browser at all).** `curl -sL -m 25 -A "Mozilla/5.0" "$url"` piped through a python one-liner that strips `<script>/<style>` tags, unescapes entities, collapses whitespace — server-rendered pages (docs, HuggingFace model cards) come back as clean text. Verify the output actually contains page content, not a shell of the site (a JS-rendered pricing page can return just the brand name — see Pitfalls).
3. **Go direct via browser.** `new_tab("https://<known-url>")` and read `document.body.innerText` via `js()`. Guess plausible paths from the site's footer/nav names before searching for them.
4. **On 403 'Forbidden / Guru meditation':** the page is fine, the browser's egress IP is blocked. Retrying the URL, waiting, or opening a new tab will not help. Route through a reader proxy: `goto_url("https://r.jina.ai/<original-url>")`, then sleep 10–15 s and read the body — it returns the page as markdown with links intact. Caveat: sites that hard-block proxy/datacenter ranges (Reddit is the canonical case) 403 through reader proxies too — after one proxied attempt confirms the block, stop; do not vary the URL, user-agent, or proxy.
5. **On captcha walls (Yandex SmartCaptcha, DuckDuckGo bot-check):** dead end — never attempt to solve or click through, and the wall fires for plain curl too (Yandex Cloud serves SmartCaptcha to any non-JS client). Fall back to step 4 for the target page directly; if that also fails, report the figure as 'unverified, needs manual check' in the final answer instead of filling it from memory.

## Pitfalls

- `goto_url` may raise `Page.navigate timed out after 5s` **while navigation actually succeeds**. Wrap it in try/except, sleep 10–15 s, then check `page_info()` / body text before declaring failure. Never conclude a page is unreachable from this error alone. If the timeout repeats across calls, the daemon itself is wedged (an unreachable/slow host can block it) — call `ensure_real_tab()` to recover before retrying the URL.
- Reader-proxy responses are cached by URL: a second fetch can return a shorter/older snapshot. Read whatever arrived fully (`len` first) before deciding the page is truncated.
- When a degraded backend returns only brand homepages or unrelated locale pages for brand-name queries, the query text is not the problem — stop rephrasing and jump to direct fetches. Pricing/landing pages are typically JS-rendered and return nearly empty via curl; the site's /docs pages are usually server-rendered and fetch fine.
- A broken backend can return confident-looking garbage: real titles, real URLs, sane descriptions — all unrelated to the query. Check the first result's title against the query before spending any calls on the results; 'results came back' is not evidence the search ran. One reformulation is enough to test this, not two.
- Search snippets are not verification of a price or spec. If direct fetches all failed, say so in the answer and label the number unverified — a confident wrong price is worse than an honest gap.
- Auto-routed search backends silently drop `site:` and other operators: an operator-heavy query returns the site's homepage or generic top results, which reads like a failed search when it is a failed operator. Rewrite the constraint as words in the query ('reddit thread about <topic>') or use a keyword-style query, not boolean syntax.
- A hard 403 site (Reddit-type 'network policy' block) fails identically via raw JSON endpoints, old./www. variants, custom user-agents, and reader proxies — these are one block, not five problems. Make one proxied attempt, then source the content elsewhere and say in the answer that the platform itself was unreachable.
- Keyword homophones are a trap for RU retail/tech queries (site names like DNS/ДНС collide with networking terms). Prefer exact site URLs and on-site navigation over general web search for such targets.
