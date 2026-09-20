---
name: hermes-config-tuning
description: "Use when tuning Hermes config: models, fallbacks, retries, MCP servers (add/verify/use)."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [hermes, config, models, fallback, parallelism, stability, mcp]
---

# Hermes Config Tuning

## When to Use

- Adding/removing models or providers (incl. OpenAI-compatible mirrors like CometAPI).
- Configuring fallback chains, retry behavior, or parallelism (tools, delegate_task).
- Diagnosing stability issues (empty responses, provider flakiness, slow failover).
- Any "how do I set X in Hermes" config question — after the bundled hermes-agent skill.
- Cost questions: provider/model price comparisons, reasoning_effort settings.

Companion to the bundled `hermes-agent` skill: hard-won operational facts for
tuning a live Hermes install. All settings go through `hermes config set` —
never hand-edit config.yaml (a stray indent corrupts it and breaks the live gateway).

## CLI facts that save debugging

- **`hermes config set KEY <yaml>` accepts complex values.** Inline flow-style
  YAML works: `hermes config set providers.foo.models "[{id: m1},{id: m2}]"`.
  No need to hand-edit the file for model lists.
- **String-list values need per-element quotes.** `hermes config set
  x.args '[-y, @scope/pkg]'` stores a plain STRING (warning: "looks like a
  list/mapping but is not valid YAML/JSON") that isinstance-gated readers
  silently ignore — e.g. an MCP server would launch without its args.
  Quote each element: '["-y", "@scope/pkg"]' → real YAML list. Confirm
  with `hermes config get` that items render on their own lines, not the
  CLI's success line.
- **Venv path is `~/.hermes/hermes-agent/venv/bin/python3`** (NOT `.venv`).
  System python lacks PyYAML — use the venv python for any yaml inspection:
  `~/.hermes/hermes-agent/venv/bin/python3 -c "import yaml; ..."`
- Install method check: `hermes --version` prints install dir + method (git).
- Verify writes by re-reading config with the venv python + yaml, not by
  trusting the CLI's success line.
- **`hermes config set model.aliases.<name> "provider/model-id"`** creates
  `/model <name>` shortcuts (verified v0.20.5). Keep alias keys clean
  (kimi3, qwen38max) — prices belong in the model display `name`, not the alias.
- **Security scan flags `curl | python3 -c` as HIGH** (pipe-to-interpreter),
  which costs an approval round-trip or blocks the call. Download the
  response to a file first, then parse the file with the venv python —
  same result, no approval friction.

## Fetching Hermes docs beyond the bundled skill

- When a Hermes question needs doc detail the bundled skill lacks, go
  straight to the markdown source: `web_extract` on
  `github.com/NousResearch/hermes-agent/blob/main/website/docs/<path>.md`
  returns the full page (all sections, ~100KB pages included). The docs
  site itself WAF-blocks plain curl and serves web_extract only a stub —
  don't burn calls retrying the site; grep the returned text by section
  title and print only the relevant slice.

## Reasoning effort (a cost lever that often does nothing)

- `agent.reasoning_effort` accepted values: minimal, low, medium, high,
  xhigh, max, ultra (`none` disables). Set with
  `hermes config set agent.reasoning_effort <value>`, verify with
  `hermes config get agent.reasoning_effort`.
- **`hermes config get agent.reasoning_effort` prints a misleading warning** ('not a recognized config key — did you mean agent.reasoning_echo') — the CLI validator just doesn't list it; the runtime DOES read it. Verify with the venv python instead: `resolve_reasoning_config(_load_gateway_config(), '<model>')` from hermes_constants/gateway.run → `{'enabled': True, 'effort': '...'}`.
- **Per-chat reasoning does not exist in config**: `platforms.<name>.channel_overrides` supports only model/provider/system_prompt (gateway/config.py ChannelOverride). Chat-level depth = `/reasoning <level>` session override; cross-chat = global `agent.reasoning_effort` or per-model `agent.reasoning_overrides.<model>`.
- **Z.ai GLM-5.3 wire format**: the zai provider plugin sends `extra_body.thinking = {"type": "enabled", "effort": <level>}`; GLM-5.3 rejects `thinking:disabled` (error 1210) so 'off' clamps to `low` — thinking can be minimized but never fully disabled on 5.3.
- **CRITICAL:** Before promising savings, verify the PROVIDER honors the parameter. Many mirrors silently drop it — CometAPI ignores `reasoning_effort` AND `reasoning` on `glm-5.3-flash` (see references/cometapi.md), so there the setting is cosmetic. Z.ai/GLM-5.3-flash DOES honor it (tested live), but only on the main model; auxiliary models (vision, compression, etc.) use their own provider/model settings — switching them to Z.ai uses `glm-4.5-air` by default unless explicitly set to `glm-5.3-flash`.
- **Pitfall:** Do not assume `reasoning_effort` works on any provider until verified. Always test with live requests (low vs high) and compare usage/billing. When a provider drops the parameter, it is not a bug; it is a feature gap. The user's server runs `low` — right cost preference, zero real effect on CometAPI-only setups.

## Cost decisions: measure real usage first

- Never price a switch from headline rates alone. Pull real usage from
  `~/.hermes/state.db`, table `session_model_usage` (python `sqlite3`
  module — the sqlite3 CLI is not installed): per model, sum
  input_tokens / output_tokens /cache_read_tokens / reasoning_tokens over
  the first_seen..last_seen span. `estimated_cost_usd` stays 0 — ignore it.
- **Cache-read tokens dominate agent workloads (measured ~10× fresh input):
  a comparison that omits the cached-input rate can flip the winner.**
  Monthly projection = span total × (30 / span_days).
- **Coding Plan vs PAYG:** Z.ai Coding Plans (Lite $18, Pro $56-80) include
  credit quotas that reset weekly. Compare your real credit usage (not token
  count) against plan tiers. If your usage is near the edge, PAYG is often
  cheaper due to the rigidity of credit windows. Always model usage over
  several billing cycles before switching — Lite may seem cheap but is often
  insufficient for real workloads.

## Price-performance model selection

- Use **Artificial Analysis Intelligence Index** (AA Index) as the standard
  benchmark for price/quality tradeoffs — higher is better. Pull the
  model comparison table from `https://artificialanalysis.ai/models` and
  cross-reference your real usage with per-model pricing.
- **Flash-class models often dominate value:** GLM-5.3-Flash (AA 42),
  DeepSeek V4 Flash (AA 25) — their lower intelligence is offset by
  10–20× lower cost per token. Never upgrade to full models unless
  the AA Index gain justifies the cost jump (e.g., GLM-5.3 full AA 45
  costs 4× more for +3 points — rarely worth it).
- **Hybrid workflow for $100 budget:** Use GLM-5.3-Flash for 90% of tasks
  ($60/mo at your usage), manually switch to full GLM-5.3 for hard
  problems (debug, architecture, refactoring) — total ~$110/mo for
  +3 AA intelligence on complex workloads.
- **Provider switching:** Vendor-direct APIs (z.ai, deepinfra, etc.) often
  beat mirror services (CometAPI, OpenRouter) on cache-read pricing
  even with higher headline input rates — verify with real usage data.

## Verified internals (v0.20.5, check current source before citing)

| Setting | Default/constant | Where |
|---|---|---|
| Parallel tool workers | `_MAX_TOOL_WORKERS = 8` — code constant, NOT configurable | `agent/tool_executor.py` |
| delegate_task children | `delegation.max_concurrent_children` (default 3, no hard ceiling; >10 logs a cost warning that caps nothing) | config |
| App-level API retries | `agent.api_max_retries: 3` | `hermes_cli/config_defaults.py` |
| Empty-response guard | `agent.empty_response_guard.enabled: true`, drops retry budget 3→1 when an empty attempt ≥ $0.25 (`cost_threshold_usd`) | same |
| Aux (background) calls | `auxiliary.transient_retries: 2`; each task pinned SEPARATELY via `auxiliary.<task>.provider` + `auxiliary.<task>.model` — there is NO global `auxiliary.model` key (v0.20.5 rejects it) | same |
| Jittered backoff | Built in (`agent/retry_utils.py`): jitter, Retry-After parsing, anti-thundering-herd lock | code |
| Retry DELAYS | NOT configurable — no config key. Hardcoded `jittered_backoff(...)` call sites in `agent/conversation_loop.py`: API errors base 5s cap 120s, empty responses base 5s cap 60s, rate limits base 2s (or server Retry-After). Shortening them = source patch (lost on `hermes update`) or upstream PR | code |

## Stability tuning recipe

1. **Fallback chain is the #1 stability win.** Default install has ZERO
   fallbacks (`hermes fallback list`). Add via `hermes fallback add`:
   a fast model on a DIFFERENT transport/provider first.
2. **With fallbacks configured, set `agent.api_max_retries` to 1** — the
   default's own comment says so: 3 in-process retries burn 30s+ BEFORE
   failover starts. (Inverse: if the user deliberately runs single-provider
   with NO fallbacks, raising `api_max_retries` is the correct lever instead —
   don't re-pitch fallbacks to a user who declined them; check
   `hermes fallback list` + their reasoning first.)
3. **Pin cheap aux work**: each aux task has its own keys — set
   `auxiliary.<task>.provider` and `auxiliary.<task>.model` per task (tasks:
   vision, compression, skills_hub, approval, mcp, title_generation,
   memory_query_rewrite, profile_describer, goal_judge, curator, monitor,
   background_review, moa_reference, moa_aggregator, review — enumerate from
   `config_defaults.py`, don't work from memory; there is NO global
   `auxiliary.model` shortcut).
4. **Do NOT**: hand-write exponential delays into config.yaml (duplicates
   built-in backoff), raise tool workers (code fork, and API latency is the
   bottleneck anyway), or raise max_iterations (burns budget on wedged tools).

## Model/provider management

- Custom OpenAI-compatible providers: `providers.<name>` with `base_url`,
  `key_env`, `models` list, `default_model`. Anthropic-transport mirrors use
  the Anthropic `/v1/messages` endpoint.
- Refresh a provider's catalog: GET `$base_url/models` with the bearer key
  (source the key from `~/.hermes/.env`), filter by
  `supported_endpoint_types` — image/audio models appear alongside chat ones.
- After changing models, smoke-test each NEW model with one real API call
  before telling the user it works.
- **User wants prices visible at model-pick time.** When adding models with
  known pricing, set a display `name` alongside `id` in the models list:
  `{id: kimi-k3, name: 'Kimi K3 in2.4/out12'}` (USD per 1M tokens, in/out,
  one decimal). API keeps using the clean `id`; the price shows in the
  picker. `/model` aliases stay clean too (`kimi3`), prices live only in
  the display `name`.

## MCP servers (mcp_servers.*)

- Add a stdio server via CLI only: `hermes config set
  mcp_servers.<name>.command npx`, `.args '["-y", "<pkg>"]'` (per-element
  quotes — see CLI facts), `.enabled true`.
- Verify the package BEFORE restarting Hermes: pipe one JSON-RPC initialize
  into it and require a result line —
  `(echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}'; sleep 4) | npx -y <pkg> 2>/tmp/err.log | head -c 600`.
  Catches a wrong package name/version in seconds and reveals the server's
  own instructions (domain rules like "fetch identifiers before use").
- **`mcp_servers.*` edits apply on Hermes restart, not mid-session** — new
  tools stay invisible to tool_search until then; verify after restart
  before promising them. For one-off urgent work while waiting: drive a
  native app directly (Calendar → see apple-calendar skill), or drive an
  HTTP MCP server raw (next bullet).
- **HTTP MCP server: add, verify, and use before restart.**
  - Add via `hermes config set`, NOT `hermes mcp add --auth header` — the
    CLI prompts for the token with getpass, which a non-TTY agent session
    cannot answer, so the add aborts with the token lost. One inline object
    does it: `hermes config set mcp_servers.<name> '{"url":"https://host/mcp","headers":{"Authorization":"Bearer <token>"},"connect_timeout":60,"enabled":true}'`,
    then `hermes mcp test <name>` and require "✓ Connected" + tool list.
  - Verify endpoint AND token in one shot before writing config: POST a
    JSON-RPC `initialize` with `Accept: application/json, text/event-stream`
    and the Authorization header — HTTP 200 + an `mcp-session-id` response
    header proves both.
  - In-session fallback before restart: call tools raw over JSON-RPC —
    `initialize` (save the `mcp-session-id` response header), POST
    `notifications/initialized`, then one `tools/call` per action, every
    POST repeating the session-id header. Build and quote the curl args in
    execute_code (python list → shell), not as a hand-typed shell line.
- **`hermes mcp login <name>` (OAuth) from a headless server**: the command
  prints an authorize URL and listens for a callback on `127.0.0.1:<port>`
  OF THE SERVER — but the browser runs on the user's machine, so SSH-forward
  the callback port(s); the provider may redirect to a different nearby port
  than advertised (observed 27890 → 27891), forward BOTH. The listener dies
  after ~5 min — run the login in tmux, and copy the FULL authorize URL from
  a WIDE tmux pane: terminal wrapping truncates these very long URLs and a
  truncated URL fails the consent page. The user opens the URL, approves, and
  pastes the final `127.0.0.1:<port>/callback?...` URL; tokens then land in
  `~/.hermes/mcp-tokens/<name>.json` (access + refresh, auto-refreshed).

## Display settings for minimal noise

- **Reactions:** Enable `platforms.telegram.extra.reactions: true` for visual acknowledgment (👀👍👎) instead of text spam. Requires gateway restart.
- **Tool progress cleanup:** `display.cleanup_progress: true` deletes technical messages after successful responses. Failed runs retain breadcrumbs.
- **Tool verbosity:** `display.tool_progress: off` (Telegram default) hides tool execution messages; combine with cleanup_progress for minimal noise.
- **Reasoning output:** `display.show_reasoning: false` (default) keeps responses clean; enable only for debugging.

## Pitfalls

- `/model <name>` is session-scoped; persist with `hermes config set model.default`.
- `hermes config get` returns `Config key not set` for defaults that still
  apply — check `config_defaults.py` before assuming a value is missing.
- Gateway/config edits apply on new sessions, not mid-conversation.
- CometAPI specifics (endpoints per transport, catalog filtering, model
  refresh workflow, current install state): see `references/cometapi.md`.
- **Telegram UX settings require restart** — `hermes config set` changes only apply after `systemctl --user restart hermes-gateway`.
