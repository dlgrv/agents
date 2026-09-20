---
name: harness-security-audit
description: "Use when auditing the user's harness (mac + VPS) security."
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [security, audit, hardening, tailscale, macos, vps]
---

# Harness Security Audit (mac + server)

Recurring user-requested audits of the personal agent harness: Hermes desktop
on the Mac, Hermes gateway on the VPS, plus adjacent surfaces (Uptime-Kuma on
cate, Telegram bots, secrets, tailnet). The user asks for a fresh external
review periodically — run the checklist, do not re-litigate accepted risks.

## Procedure
1. Re-verify closure of ALL findings from previous rounds FIRST (regression
   check, per references/audit-checklist.md) before hunting for new ones.
2. Dispatch ONE subagent for breadth: give it the full scope (both machines,
   cate, bots, secrets, tailnet) and require severity + evidence per finding.
   Child summaries are self-reports — re-verify every load-bearing finding in
   the main thread (run the exact command yourself) before telling the user.
3. Apply server fixes directly (root via SSH), verifying each one after the
   fact (binding, env, perms, service still healthy).
4. Report in Russian, grouped 🔴 fix now / 🟡 worth doing / 🟢 accepted risk;
   carry every previously accepted risk into the report explicitly so it is
   visible the user already ruled on it.

## Accepted risks — do NOT re-flag, do NOT touch
- **Clash Ghost (mihomo) on the Mac: never edit its config, secret, ports,
  never restart it.** A silent "hardening" edit broke the live proxy and
  needed a config rollback. Proxy-adjacent proposals: ask first, change
  nothing silently.
- AirPlay Receiver (ports 5000/7000) stays ON — user casts screen/audio to
  this Mac.
- Arc CDP on 127.0.0.1:9222 stays — user accepted.
- macOS application firewall stays OFF (State=0) — user accepted.
- dlgrv/agents repo is public; docker pulls go via proxy 127.0.0.1:17890.
- Telegram bot with root reach: mitigated by the bot reacting only to the
  owner in a private chat/group — re-check that restriction each audit, but
  treat the pattern itself as accepted.
- macOS-side changes needing sudo (launchctl, pf, application firewall):
  list the exact commands and let the user run them — never apply silently.

## Gates
- Every fix gets read-back verification of the exact target AND a functional
  check (gateway answers, dashboard loads, bot pings) before reporting done.
- New listeners discovered during audit: map each to the accepted list before
  calling it a finding — the harness has many intentional local ports.
