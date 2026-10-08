---
name: programmatic-adtech
version: 1.0.0
author: hermes
license: MIT
description: Use when researching or building SSP/DSP/RTB ad-tech.
metadata:
  hermes:
    tags: [adtech, ssp, dsp, rtb, vast, github-audit]
    related_skills: [github]
---

# Programmatic ad-tech research & platform building

## When to Use

Use for programmatic ad-tech tasks: explaining or building SSP/DSP/Ad Exchange, OpenRTB, VAST/VPAID video ads, or auditing open-source ad-tech projects on GitHub.

Context: Leonid is planning his own SSP + Ad Exchange (Go-only stack). Colleagues referenced Bidster/Stack (stack.bidster.net) as the demo platform and 'start with VAST/VPAID like AdFox' as the MVP scope.

## Domain primer (always-on)

- SSP = sell side (publisher traffic in, auction out); DSP = buy side (campaigns in, bids out); Ad Exchange = the RTB auction between them. One product often plays several roles — classify by which side the user enters, not by marketing labels.
- VAST/VPAID are delivery protocols (XML video-ad markup player←exchange), not platforms. 'Start with VAST' = flat-CPM tag serving, no real-time auction — the standard MVP before RTB.
- Revenue model: revshare with publishers (SSP keeps ~10-20%), markup on demand, and traffic arbitrage (buy flat low, sell RTB high) — the last is what small SSPs actually live on.
- Two-sided network: demand must exist before publishers will stay. MVP order = tag serving + direct campaigns first, auction engine second.

## Auditing open-source ad-tech on GitHub (procedure)

1. Enumerate candidates: `web_search` for the domain + 'github', then GitHub search API:
   `curl -s 'https://api.github.com/search/repositories?q=<terms>+language:go&sort=stars&per_page=15'`
2. Parse API output with **jq, never `json.loads`** — GitHub API responses contain raw control characters in descriptions that break strict parsing even with `strict=False`.
3. For each candidate fetch `/repos/{owner}/{repo}` and record: stars, forks, language, `license.spdx_id`, `pushed_at`, `archived`. Pushed >2 years ago = dead; read as reference only, never build on it.
4. License gate BEFORE recommending: AGPL/GPL forces opening your modifications when run as a service; licenses that say 'personal/internal use only' (e.g. sspserver) are unusable for commercial work; `spdx_id: NOASSERTION` means read the LICENSE file manually before trusting it.
5. Verify org-wide too (`/orgs/{org}/repos`) — the flagship repo often has sibling UI/campaign-manager repos that complete the picture.
6. Star counts < 15 mean zero production users: treat as unproven regardless of feature list; check that 'planned' integrations are not just empty interfaces.

## Key landscape finding

There is NO mature open-source 'SSP under key' — the market is closed because the margin IS the product. The viable Go assembly is: own thin layer (admin, publisher cabinet, VAST endpoint, billing) + Prebid Server (Go, Apache-2.0) as the auction core + prebid/openrtb for protocol types. Details and per-project verdicts: references/go-oss-landscape.md

## Communication style for this user

Explain in plain Russian, step by step, with concrete numbers (latencies, revshare %, timelines). ASCII diagrams of money/data flow work well. Answer the actual question ('what do we build, how does it earn') before any tooling detail.