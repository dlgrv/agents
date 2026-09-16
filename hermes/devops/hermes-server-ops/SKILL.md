---
name: hermes-server-ops
description: "Use when Hermes runs on a remote VPS: migration, Telegram."
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [hermes, vps, deployment, migration, telegram]
---

# Hermes Server Ops

Class skill for hosting the user's Hermes Agent on a remote VPS with the
desktop app and Telegram as clients. Hands-on work with user-provided SSH
creds — distinct from `vps-infra-ops` (production estate: audit mode, no
self-SSH). The Hermes VPS is a standing machine with key auth set up during
deployment; confirm the current IP with the user or shell history before
connecting.

## Architecture (correct the user's mental model every time)
- The agent is a PROCESS: everything (sessions, skills, memory, tools)
  happens on the machine where it runs. Desktop and Telegram are only
  windows to that process.
- There is NO sync between a local install and the server install. Once the
  desktop points at the server, the server is the single source of truth and
  the local copy is effectively retired. When the user says
  "синхронизация", correct to «сервер — мозг, десктоп — окно».
- Telegram and desktop talk to the same server process, so sessions created
  in one are visible in the other.

## Sizing (user-accepted baseline)
2 vCPU / 4 GB RAM / 30–40 GB NVMe, Ubuntu 24.04. Geo: Amsterdam/Frankfurt —
low Telegram latency + EU payment rails (~€4–6/mo CX22-class). No RAM
padding — the user rejects «запас на вырост» (same stance as vps-infra-ops).

## Migration procedure (local install → fresh VPS)
1. Collect creds (user pastes IP/user/password); install Hermes on the VPS
   first, same install method as the bundled hermes-agent skill documents.
2. Stop the hermes service, then copy state: `~/.hermes/skills/`,
   `memories/`, `sessions/` (incl. state.db), `cron/`, `config.yaml`,
   `.env`. Preserve `.env` mode 0600 and the service user's ownership. Tar
   up the server's fresh `~/.hermes` before overwriting — never risk the
   user's only copy of skills/chats.
3. MCP: config moves with config.yaml, but imported ≠ working. After
   restart, enumerate each configured MCP's tool list; OAuth-token MCPs may
   need re-auth even though the config migrated. Smoke-test before
   declaring done.
4. Point the desktop at the server and verify with a KNOWN session title
   from the old install appearing in the session list — that proves the
   state.db migration, not just connectivity.
5. Verify counts server-side: /skills output vs the local list, session
   count via state.db. Report both numbers to the user.

## Migration procedure (existing server → new server)
1. On new server: install Hermes fresh, run `systemctl --user enable --now hermes-gateway` to start minimal instance.
2. On old server: stop gateway, then compress full state: `tar -czf hermes-state-$(date +%Y%m%d-%H%M%S).tar.gz ~/.hermes`.
3. Transfer state: `scp hermes-state-*.tar.gz root@<NEW_IP>:/tmp`.
4. On new server: stop gateway, extract, replace: `tar -xzf /tmp/hermes-state-*.tar.gz -C ~/.hermes --strip-components=1`.
5. Restart gateway: `systemctl --user restart hermes-gateway`. Verify provider, skills count, session count, Telegram polling.
6. On old server: confirm no Hermes processes remain, optionally shut down.
7. On user's Mac: update SSH config to point to new IP, test connectivity.
8. Test Telegram/desktop sessions continuity: look for old session titles in new server's session list.

## Telegram specifics
- `/sessions` lists only the LAST 10 sessions and takes no page argument —
  the positional argument is a session NAME and acts as /resume. Older
  sessions: /resume <exact name>, or query the server's state.db.
- No dedicated «show pinned» command exists; pin state is a flag in
  state.db — answer such questions by querying it server-side.

## Config state after deployment
- Provider: Z.ai `glm-5.3-flash` (main model), `glm-4.5-air` (all auxiliary tasks except vision), `glm-5.3-flash` (vision) — all via Z.ai direct API (`https://api.z.ai/api/pas/v4`).
- `agent.reasoning_effort: medium`, `agent.max_tokens: 32768`, `agent.max_turns: 40` (user-set; medium functional since v0.21.2). NOTE: CometAPI silently ignores reasoning params entirely (verified live — no token gradient); Z.ai accepts the native `thinking:{type,effort}` and Hermes' zai plugin maps `reasoning_effort` correctly.
- Toolsets: web, browser, terminal, file, code_execution, vision, skills, todo, memory, session_search, clarify, delegation. Disabled: computer_use, connections, cronjob, tts, image_gen, video, video_gen, x_search, homeassistant, spotify, yuanbao, a2a (usage-audit: zero calls in 5 months).
- `agent.max_turns: 30` (user-set for session depth control).
- MCP: GitHub (token), Cloudflare (OAuth), Chrome-local (disabled) — verified working post-migration.
- **No CometAPI in use** — all services moved to Z.ai for cost and cache-read savings.
- **Telegram UX:** Reactions now DISABLED (`platforms.telegram.reactions: false`, flipped 2026-09-13)., `display.cleanup_progress: true` (deletes 🐍-tool bubbles after successful final answer), edit streaming (`gateway.streaming.transport: auto` — drafts don't work inside forum topics, auto-degrades), rich_messages, clarify buttons, model picker. Teacher prompt for the English-learning group via `platforms.telegram.channel_prompts["<group_id>"]`; group in `group_allowed_chats`; bot is group admin (privacy mode satisfied).
- Security hardening: ufw deny-incoming with 22/9119/4173, fail2ban (sshd jail), X11Forwarding no (sshd_config.d drop-in). Dashboard 9119 stays public (desktop connects via public IP; basic-auth gate). Tailscale = future option to close 9119.
- Z.ai 1210 handling is UPSTREAM since v0.21.2 (3bef6b6a): zai plugin folds `reasoning_effort` into `thinking` for GLM-5.3+ (medium/high/max verified live) and error_classifier matches the 1210 wording. Issue NousResearch/hermes-agent#108311 closed by us 2026-09-13 with verification (zero 1210 in gateway logs, live medium one-shot OK). No local patches to re-apply — after future `hermes update` just confirm 1210 still matches: `grep -c "cannot be disabled" /usr/local/lib/hermes-agent/agent/error_classifier.py`.
- Z.ai direct API notes: `glm-4.7-flash` (free tier) 1305-overloaded and absent from /models on pay-as-you-go keys — use `glm-4.5-air` for aux. Cache-read is the dominant cost lever (user: ~10:1 cache:input ratio); cache discount only on Z.ai direct, not CometAPI.
- Compression tuning (2026-09-13): `compression.threshold_tokens: 200000` (auto-compress long chats at 200k instead of 500k — biggest cache-read saver), `compression.progress_notices: true` (TG statuses).
- Pre-flight validation gap: `hermes config check` validates schema but NOT semantic placement (a valid-key-wrong-location like extra.reactions passes); `hermes doctor --live` probes tool backends, not platform UX flags. To verify a telegram extra actually landed, check the gateway process env: `cat /proc/$(pgrep -f 'gateway run')/environ | tr '\0' '\n' | grep TELEGRAM_*`.
- Restart pattern: agent inside the gateway process CANNOT restart it (blocked + SIGTERM kills self). Config edits need a user-run `systemctl --user restart hermes-gateway` from SSH. Batch ALL config changes before asking for one restart.

## Migration state post-move
- Verify server identity: `hostname`, `hostname -I` should match new IP
- Check SSH key trust: `ls ~/.ssh/authorized_keys` should include user's `hermes-mac` key
- Test provider connectivity: `hermes -z "Ответь одним словом: работает?"` (should return Да)
- Verify session continuity: `sqlite3 ~/.hermes/state.db "SELECT COUNT(*) FROM sessions"` should match old server's session count
- Check gateway logs for Telegram polling: `grep -E 'telegram|polling|error' ~/.hermes/logs/gateway.log | tail -3`
- Confirm dashboard port: `ss -tlnp 2>/dev/null | grep :9119` should show 0.0.0.0:9119
- Validate skills count: `ls ~/.hermes/skills/ | wc -l` should match expected number
- Verify no old server processes remain on new server (should only be new server's processes)

## New server (2026-09-13): hermes-vm
- Hetzner Falkenstein, 178.104.217.93, 7.6GB RAM / 75GB disk, Ubuntu 26.04; tailnet name hermes-vm. Tailnet IPs: server=100.93.178.88, macbook-pro=100.120.180.25.
- SSH: password auth OFF (keys only); user's Mac key 'hermes-mac' in authorized_keys. Old server decommissioned after burn-in.
- Dashboard 9119 bound to 100.93.178.88 via systemd drop-in ExecStart override (--host 100.93.178.88, hermes-dashboard.service.d/bind-tailscale.conf) + ufw 9119 public rule deleted; tailnet-only. A2A inbound enabled port 9900, peer token in .env (A2A_PEER_TOKENS=mac:...), outbound a2a toolset enabled, a2a_agents.mac -> http://100.120.180.25:9900 (gateway restart pending). Mac-side A2A setup pending.
- Tailnet route via DERP(hel) ~60-100ms, P2P not established (mac behind VPN/NAT) — fine. Server IP often blocked from RF; tailnet-over-443 is the workaround.

## Pitfalls
- Telegram UI questions («как посмотреть X»): answer by grepping the Hermes
  telegram module / state.db on the server — command behavior like the
  /sessions limit is code, not docs; guessing syntax costs a round-trip.
- Don't describe desktop↔server as sync in any written instructions — the
  word invites the user to edit «both sides» and lose changes.
- Migration validation: Always verify session count and skills count match the old server BEFORE declaring migration complete. If session count drops, the state.db transfer failed.
- SSH key rotation: When user migrates their key (e.g. from ~/.ssh/id_rsa to ~/.ssh/hermes), ensure the old key is removed from new server's authorized_keys to prevent confusion during future debugging.
- Gateway restart requirement: Any config change that affects Telegram (reactions, compression, etc.) requires `systemctl --user restart hermes-gateway` — agent-level restarts are insufficient and will be blocked.
## Honcho stack (updated 2026-09-16)
- Stack runs as docker project `honcho-local` (profile `local`); DATA volumes: old project was `local` (local_pgdata) — data restored into `honcho-local_pgdata` from /root/honcho-backup-2026-09-16.sql
- `honcho start` re-renders docker-compose.yml from TEMPLATE in site-packages honcho_cli/local/templates/ — env keys do NOT override hardcoded environment (compose environment > env_file). Hardening (passwords, ports removal) must be patched IN THE TEMPLATE; backups: /root/compose-template-backup.yml
- managed_env (env.py) originally forced AUTH_USE_AUTH=false on every render — patched to respect existing .env value
- .env keys: API_BIND=100.93.178.88, POSTGRES_PASSWORD, REDIS_PASSWORD, AUTH_JWT_SECRET (extra keys survive render)
- pg_hba: host all all all scram-sha-256 (was trust); ALTER USER postgres applied
- JWT BUG in honcho image: generate_jwt.py writes exp as ISO-string, but pyjwt decode requires int exp → "Invalid JWT"; and int exp → app parse_datetime_iso 500. WORKAROUND: token WITHOUT exp claim (w-scoped, no expiry) — verified 200. Token lives in /root/.hermes/honcho.json apiKey + /tmp/newtok2
- Ports 5432/6379 NOT published anymore (internal only); API only on tailnet IP; noauth API → 401 verified
- ufw: 22/tcp opened publicly on user request (2026-09-16); fail2ban sshd jail active
