# Go open-source ad-tech landscape (verified via GitHub API)

Verdicts below were confirmed by live API checks (stars, license, last push). Re-verify activity before acting on them — numbers drift.

## Foundation (build on)

| Repo | Stars | License | Notes |
|---|---|---|---|
| prebid/prebid-server | ~580 | Apache-2.0 | S2S header-bidding auction engine, active. Industry standard; NO admin/billing by design — host adds those. Written in Go. |
| prebid/openrtb | ~85 | Apache-2.0 | Official Go types: OpenRTB 2.x/3.0, AdCOM, Native 1.2. Use for own bid endpoints. |
| csimplestring/bool-expr-indexer | ~80 | Apache-2.0 | Fast boolean-expression index purpose-built for RTB ad selection (campaign targeting). Drop into own targeting layer. |
| revive-adserver/revive-adserver | ~1500 | GPL-2.0 | The classic ad server (PHP, not Go) — closest OSS analog of AdFox. Reference for direct-campaign features; GPL is a consideration. |

## Libraries (pick deliberately)

- bsm/openrtb (~291⭐) — most popular Go OpenRTB types BUT `license: NOASSERTION` — read LICENSE before commercial use. Default to prebid/openrtb instead.
- mxmCherry/openrtb (~158⭐) — Unlicense (public domain), dead since 2022.
- alicebob/ssp (~33⭐, MIT) — mock SSP for testing exchanges; useful for integration tests.
- RapidCodeLab/FakeDSP (~5⭐, Apache-2.0) — mock DSP for OpenRTB testing (RU-language docs).

## Rejected (do not build on)

- sspserver/sspserver (Go, active) — license explicitly forbids commercial use 'for other companies and partners'. Hard no.
- VOXDSP (PHP, AGPL) — niche; AGPL forces opening modifications.
- RTB4FREE/bidder + campaign-manager (Java, ~130⭐ total) — best-documented open DSP but dead (no pushes since 2022). Read as architecture reference only.
- ad-tech-group/openssp (Java, 167⭐) — real SSP (OpenRTB 2.4, auction, channels) but dead since 2022. Read as reference.
- ZenAd (TS, Apache-2.0) — functionally closest to 'SSP+DMP+VAST+OpenRTB+PMP in one' but ~3⭐/0 forks: effectively no production users; several exchange integrations are empty interface stubs.
- vanilla-rtb, rust-rtb-bidder, Volt, OpenAdsServer, Eyevinn SSP/DSP, haoduotnt/dsp — dead, educational, or unlicensed toys.

## Recommended target architecture (Go)

```
Own layer (gin/fasthttp + Postgres + Redis + Kafka + ClickHouse)
  - publisher cabinet, admin, VAST endpoint (flat CPM MVP)
  - billing/revshare, anti-fraud
  - targeting via bool-expr-indexer
Prebid Server (separate service)
  - RTB auction, bid adapters to external DSPs/SSPs
  - own inventory exposed via a bid adapter
Tests: alicebob/ssp + FakeDSP as mock demand
```

Stages: (1) VAST tags + direct campaigns (AdFox-level, weeks) → (2) Prebid Server as exchange core + adapters → (3) pacing, Deal ID/PMP, anti-fraud, ClickHouse reporting. Rust/C++ not needed: Prebid Server holds thousands of QPS in Go.
