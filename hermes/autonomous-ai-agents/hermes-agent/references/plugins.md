# Plugins — catalog, install, config

Hermes has a plugin catalog (`hermes plugins search <keyword>`, ~550 entries).
Plugins add agent tools, REST endpoints, dashboard/desktop UI, and hooks.

## Always-on rules

- **Search the catalog BEFORE writing a custom plugin.** The user prefers a
  maintained open-source plugin over self-written code — check stars
  (`gh api repos/<owner>/<repo> --jq '.stargazers_count'`) and pick the
  popular one. Writing a plugin from scratch and only then discovering the
  catalog equivalent wastes the whole build.
- **Read security-scanner flags yourself before `--force`.** The scanner
  often flags keyword/classification lists as "HIGH exfiltration" — grep the
  flagged lines; a list of legitimate provider endpoint URLs is a false
  positive. Never blind-force, never blind-refuse: review the flagged code,
  then decide.
- **Tool registrations are DEFERRED.** After `install --enable` the gateway
  reloads: gateway_commands/hooks are live immediately, new agent **tools
  appear next session** (`/reset` or restart). Don't test the new tool in
  the same session; smoke-test via the plugin's own CLI instead.
- Plugin config lives in `~/.hermes/plugins/config.json`; provider keys/secrets
  in `~/.hermes/.env`. Secrets are never printed by `setup.py status`.

## web-search-plus (robbyczgw, self-hosted preset)

Multi-provider search/extract replacement; auto-routing falls back through
the configured pool when a provider fails/times out.

**Production layout (user mandate: search load lives on the server, not the
Mac):** the plugin is installed on the SERVER Hermes (hermes-vm) only. The
Mac's Hermes uses the BUILT-IN web_search pointed at the server SearXNG
(`web.search_backend: searxng`; SearXNG on 100.93.178.88:8080 over
Tailscale, ~1 s per query) — no local plugin, no local daemons. Do NOT
reinstall web-search-plus on the Mac; verify the mac side with
`hermes config get web.search_backend` plus one curl of the server's
`/search?q=…&format=json`. A mac-side session started before the SearXNG
fix may still show stale fallback messages — a fresh session routes
directly.

1. `setup.py setup --preset self-hosted` → SearXNG + keyless Keenable, no
   paid keys. Add Brave/Serper/Exa keys later for type-based routing.
2. **Run setup.py with a Python ≥3.10** (system 3.9 dies on `str | None`
   typing): use `~/.hermes/tools/python-3.14.*/bin/python3`.
3. Self-hosted SearXNG on a private/Tailscale IP needs BOTH:
   `SEARXNG_ALLOW_PRIVATE=1` in `~/.hermes/.env` AND `searxng.base_url` set
   in `~/.hermes/plugins/config.json` (`SEARXNG_URL` env alone is not picked
   up as the provider base_url).
4. Smoke-test: `search.py --query ... --provider auto` — verify the fallback
   path (`"trying_next"` in output) actually returns results when the local
   instance is down; that is the feature the plugin was installed for.
5. A transient timeout puts the provider into a runtime COOLDOWN cache, so
   `auto` keeps routing to the fallback even after the provider recovered.
   Retest in a FRESH process (the cache dies with the process) before
   concluding the provider is broken. Direct sanity probe: curl the SearXNG
   URL exactly as the plugin builds it
   (`<base>/search?q=…&format=json&language=en&safesearch=0`) — results in
   ~1 s means the provider is fine and the miss was cooldown, not
   connectivity. (Cooldown caches may also reset on provider success.)

## GitHub stars via gh

`gh api -X PUT user/starred/<owner>/<repo>` — the `repos/<o>/<r>/star`
endpoint 404s; `user/starred/...` returns 204. Verify with `-i` status line.
