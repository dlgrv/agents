# CometAPI Provider Notes

Provider-specific detail for the `hermes-config-tuning` skill. Current as of
2026-09-07 (Claude family + install state); re-verify model IDs against the
live catalog before relying on them.

## Endpoints & transports

- OpenAI transport: `https://api.cometapi.com/v1` (chat/completions, models list).
- Anthropic transport: `https://api.cometapi.com` (v1/messages — configured
  Hermes-side as a separate provider `cometapi-claude` with Anthropic transport).
- Auth: `COMETAPI_KEY` in `~/.hermes/.env`, bearer header.
- Rate/flagging note: CometAPI enforces per-key rate limits; on parallel
  fan-out to many models at once, expect 429s — stagger or reduce children.

## Listing the catalog

GET `$BASE_URL/models` with the bearer key. Filter for chat-capable models:

```python
chat = [m for m in data["data"]
        if "openai" in m.get("supported_endpoint_types", [])
        and "image-generation" not in m.get("supported_endpoint_types", [])]
```

The catalog mixes chat, image-gen (flux, seedream, gpt-image), video (kling,
sora, veo, runway), audio/suno, embeddings, TTS/STT, and Midjourney action
endpoints — never add raw IDs without filtering.

## Model families seen (2026-08-28)

- GLM: glm-5.3, glm-5.3-flash, glm-5.2, glm-5.1, glm-5-turbo
- Gemini: 3.7-flash(+thinking), 3.6-flash(+thinking), 3.5-flash(+lite)
- Claude (Anthropic transport): fable-5-1, fable-5, opus-5, opus-4-8,
  sonnet-5, sonnet-4-6, haiku-4-5 (plus old 4.x snapshots and -thinking
  variants in the catalog — both deliberately excluded from Hermes config)
- OpenAI: gpt-5.6, gpt-5.5, gpt-5.3-codex, gpt-5.4*, o3/o4-mini
- DeepSeek: v4-pro, v4-flash, v3.2 (also -thinking/-exp variants)
- Others: grok-4.6, kimi-k3, qwen3.5/3.8, minimax-m3, doubao-seed-2.x

Thinking variants are separate IDs (`-thinking` suffix), not a flag.
Thought-only models are worse: `kimi-k2.7-code` produced zero visible output
for 40s+ (very slow TTFT) — it fails short smoke tests by design and is a
poor agent main model. If the user asks for it, add it with a caveat label;
don't silently treat the smoke-test timeout as a broken endpoint.

## Reasoning controls

- CometAPI ignores reasoning flags on glm-5.3-flash: `reasoning_effort` and
  `reasoning` both complete identically — no output or billing change
  (verified live). Don't sell effort settings as a cost lever on this
  provider; the lever that works is switching to a vendor-direct endpoint.

## Local install state (2026-09-07)

- Providers configured: `cometapi-openai` (17 models, default glm-5.3 — GLM×3,
  kimi-k3, qwen3.8-max/3.8-flash/3.5-plus with price labels, Gemini×5,
  GPT×3, DeepSeek×2), `cometapi-claude` (7 models, default claude-sonnet-5:
  fable-5-1, fable-5, opus-5, opus-4-8, sonnet-5, sonnet-4-6, haiku-4-5 —
  refreshed 2026-09-07; fable-5-1/fable-5/sonnet-4-6 smoke-tested OK).
  `kimi-k2.7-code` deliberately NOT added (thought-only, 40s+ TTFT).
- All aux tasks pinned to `cometapi-openai/glm-5.3-flash` (14 of 15 sections
  set 2026-08-28; `auxiliary.review.*` left at default — enumerate from
  config_defaults.py when completing).
- `delegation.provider`/`delegation.model` = cometapi-openai/glm-5.3-flash;
  `max_concurrent_children: 10`.
- `agent.api_max_retries` = 5. Fallback chain: intentionally NONE —
  user runs single-provider (CometAPI only) for consistency.
- Retry backoff left at hardcoded defaults (user chose "keep" over a local patch).
- Later the live install moved to the user's VPS (see hermes-server-ops);
  `agent.reasoning_effort` = low set server-side. The facts above describe
  the pre-deployment local install — re-verify against the server before
  relying on them.

## Pricing discovery

The `/v1/models` endpoint does NOT return pricing. To get CometAPI prices:
fetch each model's card on cometapi.com (site search → `cometapi.com/models/
<vendor>/<model>/`), or vendor official pricing minus CometAPI's ~20% mirror
discount. Record prices as `inX/outY` in the model's display `name`
(see SKILL.md). Prices are scraped, not from the API — they go stale when
CometAPI reprices; refresh on request, don't silently trust old labels.

### glm-5.3-flash price point (re-verify before quoting)
- CometAPI: $0.12 in / $0.40 out (−20% vs official $0.15/$0.50). Cached-input
  rate unpublished; the API does return `prompt_tokens_details.cached_tokens`,
  so caching may bill at an unknown discount.
- Zhipu direct (z.ai): $0.15 in / $0.03 cached / $0.50 out; launch promos
  (−50%) appear and expire — check the live page.
- On the user's real agent usage (cache-read ≈10× fresh input) z.ai direct
  came out 2–3× cheaper despite the higher headline input price. A switch
  offer was left open — no decision recorded; don't assume either side.

## Workflow that worked for model refresh

1. Fetch + filter catalog (script above).
2. Present old-vs-new diff to the user; let them pick exact models per provider
   and the default (clarify tool, choices per provider).
3. Apply each list with `hermes config set providers.<name>.models "[{id: m1},...]"`
   and `hermes config set model.default <id>`.
4. Smoke-test each NEW model with one real API call (OpenAI: chat/completions
   with max_tokens ~50; Anthropic transport: /v1/messages + x-api-key +
   anthropic-version header). GLM reasoning models may return only
   `reasoning_content` within a small token budget — that still proves reachability.
5. Read back EVERY touched surface to confirm final state: Hermes config via
   venv python + yaml; external tools' config files (Zed settings.json is
   JSONC, opencode.jsonc) via parse. A scripted edit can silently break those
   files — e.g. removing the LAST element of an array leaves a dangling comma
   on the preceding line; the patch tool refuses JSONC outright (fails plain
   JSON validation), so use scripted line ops + validate with comment lines
   stripped (see zed-editor skill, references/free-model-catalogs.md).
