# Audit checklist — mac + Hermes VPS

## Server (root via SSH)
- sshd: `sshd -T | grep -E 'permitrootlogin|passwordauthentication|x11forwarding'` → prohibit-password / no / no
- fail2ban: `fail2ban-client status sshd` (jail active, banned list sane)
- listeners: `ss -tlnp` — cross-check every 0.0.0.0 binding against the
  accepted list; dashboard 9119 must bind the tailnet IP only
- ufw: `ufw status verbose` — only 22 public plus explicitly accepted extras
- IPv6: `ip6tables -L -n` — DROP policy present
- secrets perms: `ls -la /root/.hermes/scripts /root/.hermes/mcp-tokens ~/.hermes/.env` → 0600/0700
- watchtower: `docker inspect watchtower --format '{{json .Config.Env}}'` →
  LABEL scope only (no unscoped auto-updates of every container)
- automation inventory: `crontab -l`, `ls /etc/cron.d`, `ls /root/.hermes/scripts` — matches the known set (a2a-cleanup, logs-cleanup, …)
- Tailscale: fetch the tailnet policy via admin API — deny-by-default, only
  mac↔server grants; `tailscale status` healthy

## Mac
- listeners: `lsof -iTCP -sTCP:LISTEN -n -P` — map each to the accepted list
  (AirPlay 5000/7000, Arc CDP 9222, clash 17890, mcp-macos-calendar 8083
  tailnet-only, …)
- LaunchAgents: `ls ~/Library/LaunchAgents/ai.dlgrv.*` — standard naming,
  referenced scripts exist and are executable
- secrets perms: `~/.hermes/.env`, `~/.hermes/mcp-tokens/` → 0600/0700
- after any ACL/policy change: `tailscale status` + ping the peer tailnet IP,
  then exercise one service per grant (A2A, SSH)

## After each fix
1. Read back the exact target (config value, binding, env, mode).
2. Functional check: the primary flow still works (gateway answers, dashboard
   loads, bot responds, proxy passes traffic).
3. Record the closure state so the next audit starts from a checklist, not
   from memory.
