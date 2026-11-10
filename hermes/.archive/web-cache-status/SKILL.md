---
name: web-cache-status
description: "Status and detection of dead web caches as of 2024-2025"
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [research, archives, web, cache, dead-routes]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, archives, web, cache, dead-routes]
    related_skills: [blocked-page-recovery, grounded-citations]
---

# Web Cache Status — Dead Routes as of 2024-2025

## When to Use

Use this skill when:
- You encounter Bing or Google cache URLs in search results or user-provided links
- You need to verify if a cache URL is actually valid or a dead redirect trap
- You want to understand why cache-based recovery attempts are failing
- You need to document dead cache routes for future reference

## Dead Routes (DO NOT USE)

### Google Cache
- **Status:** Dead since mid-2024
- **URL pattern:** `webcache.googleusercontent.com`
- **Failure mode:** Returns HTTP 200 + tens of KB, but it's a Google Search interstitial with a JS redirect, not a cache. Never use it.
- **Detection:** Body contains `<title>Google Cache</title>` and JS redirect to original URL.

### Bing Search Cache
- **Status:** Dead as of 2025
- **URL pattern:** `https://www.bing.com/ck/a` with `u=a1(base64)` parameter
- **Failure mode:** Wraps results in JavaScript redirects to the original (blocked) URL. The `u=a1(...)` parameter decodes to a redirect, not content.
- **Detection:** Attempts to extract the original URL from base64 lead to redirect loops; body contains "Bilder", "Videos", "Karten", "Neuigkeiten" (German interface) or similar navigation stubs.

## Current Working Alternatives

1. **Wayback Machine** — `https://archive.org/wayback/available?url={URL}`
2. **archive.today** — `https://archive.ph/newest/{URL}` (domain rotation: .ph → .md → .li → .is)
3. **Jina Reader** — `https://r.jina.ai/{URL}` (requires `JINA_API_KEY`)

## When Encountering Bing/Google Cache Links

If a user provides a Bing or Google cache URL (or if search results point to them), do not attempt to fetch or decode them. They are not content copies — they are redirect traps. Use the working alternatives above instead.

## Detection in Search Results

Bing search results now only return HTML wrappers, not cached copies. If you see:
- `https://www.bing.com/ck/a` URLs
- Base64-encoded `u=a1(...)` parameters
- German interface elements ("Bilder", "Videos", etc.) in Bing results

These are not content sources — they are navigation stubs. Fall back to Wayback or archive.today immediately.

## Reference Files

- `references/bing-search-dead.md` — Detailed detection patterns and fallback strategies
- `scripts/cache-status-check.py` — Script to detect dead cache URLs in search results
