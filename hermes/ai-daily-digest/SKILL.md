---
name: ai-daily-digest
description: "Use when editing the AI digest cron, script, or dedup."
---

# AI Daily Digest (08:00 MSK)

## Components
- Cron job `af2df3e90195` (schedule `0 5 * * *` = 08:00 MSK, deliver: origin, continuity: on)
- Prefilter script: `~/.hermes/scripts/arxiv_digest_prefilter.py` (no LLM, zero tokens for scanning)
- Dedup state: `~/.hermes/cron/arxiv_digest_seen.json` (id -> {"sent": date, "upvotes": int|None})

## Hard rules
- LLM NEVER sees the full arXiv firehose (~112k tok/day) — only the 30-item shortlist (~8-10k tok). Keep it that way.
- seen.json marks EVERYTHING scanned (not just top-5), so dedup never leaks repeats.
- HYPE re-send rule: a previously sent paper returns only if HF upvotes grew >=10 AND current >=25 AND prev value was actually known. `upvotes: None` means "HF didn't answer" — NEVER store 0 for that (0 vs unknown caused false "0 -> 70" hype).
- Sources down => agent must send one line "sources unavailable" and MUST NOT rebuild the digest from previous run's output (continuity context contains it — replay happened once on 2026-09-20, апвоты совпали 1-в-1).
- arXiv API: submittedDate range queries silently return 0 for recent days (index lag); use sortBy=submittedDate + local date filter, window 3 days. HF Daily is empty Sat-Sun (weekend, confirmed 19-20.09) — Sunday runs legitimately end in [SILENT].
- arXiv API quirk: `cat:X AND submittedDate:"..."` works, but OR-groups of categories + submittedDate return 0. Fetch per-category.
- Politeness: 1s sleep between arXiv category requests; HF 429s quickly — wait ~90s before retry.

## Digest format (audience: beginner LEARNING the terminology)
- Top-5: **Title** — 1-2 Russian sentences using the REAL terms inline, each followed by a plain-language gloss in parens: «KV-кэш (память модели о уже прочитанном)». Never hide a term behind a paraphrase — name it, then decode it.
- Org attribution: infer from famous authors; if unsure — OMIT, never guess. Live web-search allowed to verify.
- «📚 Словарик» block: 3-6 hardest terms ALREADY USED above, one-two plain sentences each with бытовая аналогия. The glossary DEEPENS the inline glosses, not replaces them.
- Footer line: how many candidates scanned.
