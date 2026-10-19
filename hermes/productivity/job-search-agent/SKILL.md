---
name: job-search-agent
description: Use when working on Leonid's job-agent job-search pipeline.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [automation, job-search, hh]
    related_skills: [hermes-vm-stack, plan]
---

# Job Search Agent (job-agent)

## When to Use

Use when Leonid asks about, continues, or deploys the job-agent pipeline: auto job search (hh.ru, RemoteOK, WeWorkRemotely, HN Who's hiring), LLM scoring against his resume profile, autopilot apply on hh above score threshold, Telegram digest.

Full implementation plan: `~/.hermes/plans/2026-10-19_142240-job-search-agent.md` (phases, task breakdown, file paths). Code repo: primegit (NOT GitHub — resume profile and scores are private), deployed to `/opt/job-agent/` on hermes-vm.

## Standing decisions (do not re-litigate)

- **Dry-run week is a hard gate.** Leonid chose full autopilot, but live applies only start after a dry-run week where the digest lists 'would apply on' — he calibrates the threshold. One bad score = a wasted profile view in front of a recruiter.
- Autopilot guards: score ≥ 8/10, cap 10 applies/day, stop-words (1C, crypto-scam heuristics), halt + alert after 2 consecutive apply errors.
- Roles: Python backend + ML/LLM. Moscow/remote for RU; foreign = remote only, English cover letters (EN-CV at dlgrv.com/cv, RU resume on hh).
- Digest via @fafbbea_bot (token already on hermes-vm; sending with the same token is compatible with the Kuma poller — only getUpdates conflicts, and we never call it).

## Deployment rules

- Everything runs on hermes-vm via `ssh hermes-vm-ts` (direct IP is RF-blocked). systemd `job-agent.timer`, 09:00 Europe/Moscow — check `timedatectl` first; if the host is UTC, schedule 06:00 UTC.
- Secrets in `/opt/job-agent/.env` chmod 600 (TELEGRAM_BOT_TOKEN, HH_TOKEN, CHAT_ID, LLM_BASE_URL/API_KEY/MODEL — scorer calls the Hermes LLM provider directly, not local Hermes).
- **hh apply IP rule:** the hh API + OAuth token are fine from the server's foreign datacenter IP, but browser automation on hh from it invites captcha/suspicion. If the apply path ends up browser-based, the apply worker lives on the Mac (RU residential IP) and drains a `queued` status from the server DB. LinkedIn/career-ops is the reverse: server-side only, foreign IP reads as natural, and the branch stays off by default (ban risk accepted by user, ≤15 Easy Applies/day).

## Status

Planning approved; Phase 0 (spikes: hh apply path via API vs browser; remote-board sources from server IP) not yet run. Next step when resuming: run the spikes, then Phase 1 TDD build per the plan.