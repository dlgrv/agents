---
name: blocked-page-recovery
description: "Use when a fetch fails: 403/429, paywall, WAF, bot wall."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Archives, Wayback, Paywall, WAF, Fallback]
    related_skills: [grounded-citations]
---

# Blocked-Page Recovery

When a page won't fetch — 403/429, Cloudflare "Just a moment...", a paywall,
or a bot-detection interstitial — don't give up and don't loop on the same
URL. Third-party services often hold a **copy** of the page. Work down this
ladder, cheapest first.

## When to Use

- "Alert me when this laptop drops below $1,000."
- "Watch these flights for a fare under $500."
- "Tell me when this hotel has a refundable room."
- "Track ticket/listing availability."
- A cron tick fires for an existing price watch (steps 4-6).
- **Korean product research**: When brand sites are unreachable or lack purchase/shipping info, use Naver/Coupang as discovery and fallback.
- **Korean edtech/device lookup**: For brands like Wordmelon, try Smart Store search when direct site fails.

Don't use for: one-off "what does this cost right now" lookups (use `web_search`/`web_extract` directly).

## The ladder

```
1. Wayback Machine  — archive.org "available" API  (snapshot + timestamp)
2. archive.today    — domain rotation: archive.ph → .md → .li → .is
3. Jina Reader      — only if JINA_API_KEY is set  (live server-side render)
4. API-first pivot  — look for /api/, /graphql, .json, or RSS on the same host
5. Browser automation — use browser tools when JS challenge scripts are present
6. Korean e-commerce pivot — try Naver/Coupang/SmartStore for products, especially Korean brands
```

Run it in one shot with the bundled script:

```bash
python3 scripts/recover_page.py "https://example.com/blocked-article" --json
```

The script tries each route in order, validates every body (see "Fake
successes" below), and prints the first genuine hit with its provenance.

For JS-challenged pages that archives can't solve, use the browser script:

```bash
python3 scripts/browser_recovery.py "https://example.com/challenged" --wait 6
```

## Provenance discipline (non-negotiable)

Every recovered copy carries a provenance you MUST preserve when citing:

| Route | Provenance | How to cite |
|-------|-----------|-------------|
| Wayback / archive.today | `snapshot` | Cite WITH the snapshot date: "as archived 2026-08-06". Never present a snapshot as the live page — it may be stale. |
| Jina Reader | `live` | Server-side re-render of the live page; cite normally. |
| Live fetch / browser | `live` | Cite normally. |

If the user needs *current* data (prices, availability, breaking news), a
snapshot is context, not an answer — say so explicitly and note its age.

## Manual routes

### 1. Wayback Machine (best provenance, try first)

```bash
# Discovery: returns closest snapshot URL + timestamp as JSON
curl -sL "https://archive.org/wayback/available?url={URL}"
# Then fetch archived_snapshots.closest.url
```

For enumerating many snapshots (or recovering deleted pages), the CDX index:

```bash
curl -sL "https://web.archive.org/cdx/search/cdx?url={URL}&output=json&limit=10"
```

CDX intermittently returns 503 under load — if it does, fall back to the
`available` API; don't retry-hammer it.

Works for: any publicly crawled URL. Fails for: robots-blocked sites,
never-crawled URLs, JS-only SPAs (snapshots don't render).

### 2. archive.today (paywalls, deleted content)

User-submitted archives — often has paywalled news articles Wayback lacks.
Rate-limits aggressively (429) and rotates domains, so iterate:

```bash
for d in archive.ph archive.md archive.li archive.is; do
  curl -sL --max-time 20 "https://$d/newest/{URL}" -o ~/.hermes/cache/scratch/page.html \
    -w "%{http_code}" && break
done
```

**Validate the body, not the status code** — a 429 still ships several KB of
rate-limit HTML that looks like a success to a size check alone.

### 3. Jina Reader (requires JINA_API_KEY)

`r.jina.ai` re-renders the live page in a real browser server-side and
returns markdown. Anonymous access is dead (401 → Turnstile); a key is
required:

```bash
curl -s -H "Authorization: Bearer $JINA_API_KEY" "https://r.jina.ai/{URL}"
```

Handles JS SPAs that archives can't. Skip this route entirely when the env
var is unset.

### 4. API-first pivot

WAFs protect the HTML surface far more aggressively than the data endpoints
behind it. After 2-3 blocked attempts on a site, stop fighting the HTML and
look for:

- `/api/...`, `/graphql`, or `.json` variants of the page URL
- An RSS/Atom feed (`/feed`, `/rss`, `<link rel="alternate">` in any copy
  you did recover)
- A sitemap (`/sitemap.xml`) revealing canonical URLs that may not be gated

### 5. Browser automation (JS challenges)

When a page serves a JavaScript challenge (Cloudflare, Qrator) with a script that
waits for execution and sets cookies (`cf_clearance`, `qrator_jsr`), a direct
fetch or archive service will fail. The browser tool can pass these:

- **Wait for challenge completion**: Let the page load fully — challenge scripts
  often reload the page after setting cookies. Use `wait_for_load()` and
  `time.sleep(6)` after navigation to let JS execute.
- **Check for success signs**: After waiting, look for page content instead of
  interstitials. `page_info()` and `document.body.innerText` reveal if you're
  seeing the real page or still blocked.
- **Provenance**: `live` — this is the actual page content, though it may be
  delayed by challenge execution time.

**Pitfall**: Do NOT conclude you're blocked until the challenge script has
fully run. Many JS challenges serve a 200 status code but delay content
delivery — waiting is required, not a sign of failure.

### Hard IP bans vs JS challenges — identify the wall first

Before choosing a route, classify what is blocking you:

- **JS challenge** (Cloudflare, Qrator): serves an obfuscated challenge
  script, sets a short-lived cookie (`cf_clearance`, `qrator_jsr`), then
  reloads. A real browser that waits and lets the script run can pass.
- **Hard IP ban**: serves a plain 403 HTML body ("Access forbidden",
  Qrator "Guru meditation") with NO challenge script and no cookie. No
  client-side trick passes it — the block is on your network, not your
  fingerprint.

**Pitfall**: Treat all 200 responses with interstitial content as JS challenges
until proven otherwise. Never classify a page as "hard IP ban" based on
content delay; only classify it as such if the response body is a static
403/404 with no challenge script and no reload mechanism.

Before crediting a proxy as a workaround, verify it actually changes the
egress IP — a local proxy that exits via the same address reproduces the
same ban:

```bash
curl -s --max-time 10 https://ifconfig.me; echo
curl -s --max-time 10 -x http://127.0.0.1:17890 https://ifconfig.me; echo
```

If both print the same IP, skip the proxy route entirely.

## Fake successes — routes that LIE

These return HTTP 200 with a plausible body that is NOT the page. The script
rejects them automatically; reject them manually too:

- **Google Cache is dead** (since mid-2024). `webcache.googleusercontent.com`
  returns 200 + tens of KB, but it's a Google Search interstitial with a JS
  redirect, not a cache. Never use it.
- **AMP caches** (`*.cdn.ampproject.org`) mostly return a ~300-byte
  `<title>Redirecting</title>` meta-refresh stub pointing back at the
  original (blocked) URL. Treating that as success creates a fetch loop.
- **Rate-limit bodies**: archive.today 429 pages are multi-KB HTML. Check for
  the target's actual content (title words, expected strings), not just size.

Detection heuristics the script applies: body under a per-route byte floor;
meta-refresh/JS-redirect stubs whose target is the original host; interstitial
titles ("Just a moment", "Redirecting", "Google Search", "Attention Required").

## Proxy relays: don't

Generic "web proxy" relays are man-in-the-middle by construction. Never send
cookies or Authorization headers through one, and don't use them for anything
the user will rely on — provenance is unverifiable. Prefer archives, which at
least timestamp their copies.
