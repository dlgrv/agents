# Free-model catalogs snapshot (2026-09-07)

User keeps free-ONLY model lists in Zed's `openai_compatible` providers
(`openrouter-free`, `opencode-zen`). A "remove all paid, keep only free" pass
turned out to be drift-fixing: both lists already equalled the full free set.

## Catalog endpoints & free-detection

| Source | Endpoint | How to detect free |
|---|---|---|
| OpenRouter | `GET https://openrouter.ai/api/v1/models` (no auth) | `pricing.prompt == 0` AND `pricing.completion == 0` |
| opencode zen | `GET https://opencode.ai/zen/v1/models` (no auth) | NO pricing fields returned — free set is suffix-marked: `-free`, `-contributor-free`, plus `big-pickle`; everything else paid |

## OpenRouter free chat models (21 free detected, 17 chat-usable)

All `:free` suffix, 128k context unless noted:

- cohere/north-mini-code:free
- dots-studio/dots-3-note-preview:free
- google/gemma-4-26b-a4b-it:free
- google/gemma-4-31b-it:free
- inclusionai/ling-3.0-flash-fin:free
- inclusionai/ling-3.0-flash-sante:free
- liquid/lfm-2.5-2.6b:free
- minimax/minimax-m2.7:free
- minimax/minimax-m3:free
- nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free — 256k ctx, omni (text+image+audio+video→text); added 2026-09-07, smoke-tested OK
- nvidia/nemotron-3-super-120b-a12b:free
- nvidia/nemotron-3-ultra-550b-a55b:free
- nvidia/nemotron-3.5-lightning:free
- openrouter/free — no `:free` suffix (meta-router over free models)
- poolside/laguna-s-2.1:free
- poolside/laguna-xs-2.1:free
- thinkingmachines/inkling-small:free
- thinkingmachines/inkling:free

Free but NOT chat — skip:
- google/lyria-3-clip-preview, google/lyria-3-pro-preview — $0 but audio generation (modality `text+image->text+audio`)
- nvidia/nemotron-3.5-content-safety:free — moderation classifier

Removed 2026-09-07 (was in the Zed list, no longer in the catalog): `z-ai/glm-5.2:free`.

## opencode zen free models (8 = the entire free set)

big-pickle, deepseek-v4-flash-free, muse-spark-1.3-contributor-free,
muse-spark-1.2-contributor-free, mimo-v2.5-free, ling-3.0-flash-fin-free,
nemotron-3-ultra-free, nemotron-3.5-lightning-free.

Zen catalog totals ~70 models; the claude/gpt/gemini/glm/kimi/qwen ids on Zen
are all PAID — do not add them to the free list.

## Refresh procedure

1. GET both catalogs (curl to /tmp files; no auth needed for either).
2. OpenRouter: filter `pricing.prompt==0 and pricing.completion==0`; drop
   non-chat (check `architecture.modality` — exclude audio-output models; drop
   moderation/content-safety models); diff against the current Zed list BOTH
   ways — dead ids out, new free ids in.
3. Zen: free set = suffix-marked ids (`-free`, `-contributor-free`,
   `big-pickle`); diff the same way.
4. Edit `~/.config/zed/settings.json` by scripted line ops + validate (strip
   `//` comment lines → `json.loads`). Pitfall: when removing the LAST array
   element, the preceding line's comma dangles and the file stops parsing —
   check for trailing commas after any removal. The `patch` tool refuses the
   whole file for this (JSONC fails plain JSON validation) — use scripted
   replacement + validation instead.
