# Benchmarking LLM endpoint speed (TTFT + tok/s)

Companion to key validation: once a key is proven LIVE, measure how fast it
actually is. Works for any OpenAI-compatible endpoint (proxies, relays,
self-hosted vLLM). Python stdlib only — no SDK needed.

## Metrics
- **TTFT** (time to first token): wall time from request sent to first content
  chunk. Dominates perceived latency for short answers.
- **tok/s during generation**: real completion tokens / generation time, where
  generation time = total − TTFT. Report both, plus total time.

## Recipe (streaming SSE via urllib)
1. POST `/v1/chat/completions` with `"stream": true` and
   `"stream_options": {"include_usage": true}` — the final SSE chunk then
   carries `usage` with REAL token counts. Never estimate tok/s from chunk
   counts alone: many proxies batch several tokens (or whole sentences) into
   one chunk, which inflates chunk-based tok/s by 3–10x (a proxy served one
   model at a "1266 tok/s" that was really ~340).
2. Timestamp on first content delta → TTFT; on last delta → end.
3. Read `usage.completion_tokens` from the final chunk; divide by gen time.

## Pitfalls
- The final usage chunk has `"choices": []`. Index unconditionally
  (`obj["choices"][0]`) and you get `IndexError` on every request that
  includes usage. Guard: `choices = obj.get("choices") or [{}]`.
- Proxies inject SSE comment lines (`: heartbeat`, blanks) between data
  lines. Skip any line not starting with `data:`; collect them for debugging
  instead of crashing.
- `/v1/models` may list fewer/different names than advertised — a model that
  400s with `model_not_found` may simply not exist on the proxy. Enumerate
  `/v1/models` FIRST and benchmark only IDs it returns; don't trust the
  marketing list.
- Run >600s? The terminal tool auto-promotes it to a tracked background
  process with notify_on_complete — that's fine, poll/wait for it, don't
  re-run.

Reference numbers for sanity (as of late 2026): official Anthropic-style APIs
serve ~50–100 tok/s for large models; a proxy consistently exceeding ~400
tok/s per-chunk-timing is likely buffering, so weight `total_s` over tok/s.

Known-good script pattern lives in this skill's history; rebuild it in
~5 lines of urllib per the recipe above rather than hunting for an SDK.
