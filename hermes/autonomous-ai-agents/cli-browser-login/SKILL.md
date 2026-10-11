---
name: cli-browser-login
description: Use when a CLI login times out awaiting browser auth.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [cli, login, auth, browser, cursor-agent, oauth, timeout]
    related_skills: [hermes-agent, codex, github-auth]
---

# CLI Login via Browser Deep Link

## When to Use

Any CLI whose `login` subcommand prints a URL and waits for the user to finish auth in the browser, and the process times out before that can happen (cursor-agent; the same pattern applies to gh/vercel/wrangler-style deep-link flows).

Tools like `cursor-agent login` print a login URL and wait for the user to finish auth in the browser, but the process itself times out in ~10-15 seconds. Fire-and-forget in a foreground terminal always loses this race.

## Procedure

1. Start login in background with a PTY, logging to a file:
   ```
   terminal(command="cursor-agent login > /tmp/login.log 2>&1", background=true, pty=true)
   ```
2. Poll the log in a tight sub-second loop and open the URL the moment it appears. Do not wait for the process or for a foreground turn — the process will die before one round-trip finishes.
   ```bash
   for i in $(seq 1 40); do
     URL=$(tr -d '\r\n' < /tmp/login.log | grep -o 'https://[^ ]*' | head -1)
     [ -n "$URL" ] && open "$URL" && echo "$URL" && break
     sleep 0.5
   done
   ```
3. The user completes auth in the browser. The CLI process may still print `Login failed or timed out` — that is fine, see verification.
4. Verify with the tool's own status command (`cursor-agent status`, `gh auth status`, ...), never by the login process's exit message.

## Pitfalls

- Strip line breaks BEFORE grepping the URL (`tr -d '\r\n' < log | grep -o 'https://[^ ]*'`). These CLIs hard-wrap the printed link across 2-3 lines; a per-line grep catches only the head (challenge param) and misses the tail (`uuid`, `redirectTarget`) — an opened truncated link fails silently. On BSD/macOS, `tr` takes exactly two set arguments: `tr '\r' '\n' ' '` is a usage error — use `tr -d '\r\n'` or `tr '\r\n' '  '`.
- A stale `Login failed` does not mean auth failed. The browser-side flow stores the token independently of the CLI poller; if the user completed auth on any attempt's link, run `status` before re-running login — you may already be logged in.
- Read the tool's `--help` before improvising. Some logins have a non-interactive path that skips the browser dance entirely (`--api-key` / env var for cursor-agent); prefer it when the user has a key.
