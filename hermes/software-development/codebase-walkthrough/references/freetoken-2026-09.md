# FreeToken (FlashML-org/FreeToken) — walkthrough notes (2026-09-09)

Worked example of the walkthrough workflow; also a knowledge bank for follow-up questions.

**What it is**: local inference engine for MoE LLMs on consumer GPUs. Core bet: don't fit the whole model in VRAM — expert weights live in pinned host RAM; GPU keeps an LRU slot-cache and fetches/computes on demand. Serves OpenAI + Anthropic APIs from one process. ~84k LOC Python + Triton/C++ kernels, heavy test suite (91 test files mirroring package layout).

## Module map (python/freetoken/)

- `moe/` — three MoE backends:
  - **offload**: GPU LRU slot-cache (`offload_cache.py`, bank schemas per quant format: bf16, fp8_block, nvfp4, mxfp4, q4_0); decode misses copied PCIe-batch from host banks (fused multi-bank `cudaMemcpyBatchAsync` path, `FREETOKEN_FUSED_COPY=0` forces legacy per-bank).
  - **cpu**: decode GEMV on a CPU worker pool at full RAM bandwidth; whole path CUDA-graph-capturable.
  - **hybrid**: cache hits + a bandwidth-matched fraction of fresh fetches run on GPU, remaining misses on CPU; partial results summed. Fetch fraction comes from `ft bench bw` profile (`~/.cache/freetoken/benchbw/<gpu-uuid>.json`) — the README's "q* policy"; choice offload-vs-hybrid is hardware-adaptive (`engine/engine.py` + `moe/bench_profile.py`).
  - Prefill for the offload family: per-layer GPU double buffer (compute layer N while loading N+1).
- `engine/` — VRAM budget as pure integer arithmetic (`cache_budget.py`, unit-testable without GPU); `--moe-cache-auto` sizing + runtime rebuild.
- `kvcache/` — paged KV pools (mha, swa, dsa, qsa, linear-state), radix prefix cache; `hybrid_radix_cache.py` = full-attn KV + GDN state snapshots on tree nodes (mirrors sglang MambaRadixCache).
- `checkpoint/ftw.py` — FTW format: whole checkpoint as one contiguous byte region, every tensor 4096-aligned → any tensor O_DIRECT-readable; shards ≤8GiB.
- `server/` — FastAPI: `/v1/chat/completions`, `/v1/responses`, `/v1/messages`; tool-call + reasoning parsers; request logging.
- `kernel/` — Triton (fused MoE per quant format, FLA linear-attention kernels, sparse attention) + C++ ext (`cpu_moe`, pinned allocs); JIT via nvcc or prebuilt wheel.
- `models/` — loaders: qwen2/3/3.5-moe/4_exp, glm_moe_dsa, deepseek-v4, gpt_oss, llama, mistral, minimax-m2/m3.
- `scheduler/`, `daemon/`, `shell/` — chunked prefill + batching, server daemon (`ft serve` mgmt), TUI chat. `ft launch claude|codex|...` writes the agent's provider config and starts it against the local server.

## Notable engineering details (cited in the answer)

- `cudaLaunchHostFunc` submit/sync costs ~30–50µs per call (~6ms/step on a 75-layer model) → replaced with a flag handshake: GPU does `cuStreamWriteValue64` on a mapped-pinned "ready" flag, a persistent CPU coordinator polls, sets "done"; GPU waits via stream memops. No SM-resident kernel, so reported GPU util stays truthful (`moe/cpu_executor.py`).
- They first used a spin-wait kernel: it pinned utilization at 99%, laptop power schedulers responded by clamping CPU frequency → net decode regression. Fix was the memop handshake, not a perf trick.
- `cudaMemcpyBatchAsync` silently degrades to SYNCHRONOUS copy when a batch mixes large entries with sub-~256KB entries on registered host memory (H100 + CUDA 13.0, empirically bisected) → banks with smaller rows ship as one whole-layer entry so every per-run entry is ≥256KB (`moe/offload_cache.py`).
- `AGENTS.md` forbids autonomous-agent contributions: agents may not push as the user; every PR needs a human who can explain the code.

## Workflow trace (what worked)

README+quickstart via raw.githubusercontent (2 curls) → shallow clone to /tmp (11s) → one `find|sort` pass → `head -40` on 5 key modules → 3 targeted greps (q*, auto/backend resolution) → answer. No GitHub API needed; the earlier API-tree attempt hit the control-char pitfall (see SKILL.md).