---
name: ai-digest
description: Daily AI research digest with arXiv and Hugging Face Papers.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Digest, Automation, HuggingFace, Arxiv, Hype]
    related_skills: [arxiv]
---

# AI Research Digest

Deliver a daily AI research digest to Leonid at 08:00 Moscow time, sourced from fresh arXiv papers and Hugging Face Daily Papers, with smart deduplication and hype-based resurfacing of trending work.

## Quick Reference

| Task | Command | Purpose |
|------|---------|---------|
| Run one-off digest | `python3 /root/.hermes/scripts/arxiv_digest_prefilter.py` | Test pipeline manually |
| Cron job | `cronjob_manage` | Scheduled delivery (05:00 UTC = 08:00 MSK) |
| View seen papers | `cat /root/.hermes/cron/arxiv_digest_seen.json` | Track sent articles and upvotes |
| Reset seen list | `echo '{}' > /root/.hermes/cron/arxiv_digest_seen.json` | Force fresh start |

## Pipeline Architecture

1. **arXiv Fetch**: Get 3 days of papers from cs.AI, cs.CL, cs.LG, cs.MA, cs.SE (covers ML/NLP/AI/Robotics/SE)
2. **Hugging Face Daily**: Fetch today's and yesterday's HF Daily Papers (fallback: individual API calls)
3. **Deduplication**: Track sent papers and upvotes in `/root/.hermes/cron/arxiv_digest_seen.json`
4. **Hype Detection**: Resurface papers with ≥20 upvote gain since last sent (min 50 upvotes total)
5. **Model Selection**: Present 30 candidate papers to model (new + hype)
6. **Top-5 Selection**: Model picks top 5 for final digest
7. **Delivery**: Send via cron job to Telegram

## Daily Job Configuration

```bash
# Job: Утренняя AI-сводка (08:00 МСК)
cronjob_manage --action run --job_id af2df3e90195 --prompt "Ты формируешь утреннюю AI-сводку для Лёни из свежих статей. Выбери топ-5 из представленного списка. Выведи только топ-5 в формате:

1. **Название** — arXiv: ID (дата)
   Авторы: [Имя1, Имя2, ...] (организация, если известна)
   Краткий пересказ (2-3 предложения, суть)
   [HYPE: X -> Y апвотов] (если хайп)

2. ... (и так далее)

---
Источники: {count} статей arXiv за 3 дня + {count} из HF Daily.
Новых: {new}; повторов-хайпов: {hype}.
Шорт-лист ({shortlist} новых + {hype} хайпов). Выбери топ-5 для сводке:

{papers_list}"
```

## Script Details

- **Location**: `/root/.hermes/scripts/arxiv_digest_prefilter.py`
- **arXiv Window**: 3 days (avoids lag in submittedDate index)
- **HF Fallback**: If batch HF Daily fails, fetch individual papers via `https://huggingface.co/api/papers/{id}`
- **Hype Logic**: Only resurface if previous upvotes were known (not 0 from API failure)
- **Author Extraction**: arXiv authors field, compact display (≤3 names, else 'et al.')
- **Organization Detection**: Check known affiliations (e.g. NVIDIA, Google, MIT) but don't guess
- **Dedup Key**: arXiv ID without version (e.g. 2609.20519)

## Hype Detection Rules

- Minimum upvotes to qualify: 50
- Minimum growth to trigger hype: 20
- Only papers with known previous upvotes are considered for hype
- HF rate limits trigger fallback to individual paper API calls

## Format Requirements

- Headline: `☀️ **AI-сводка — [день недели], [дата] [месяц] [год]**`
- Authors: `Авторы: Name1, Name2, Name3 et al.` (if known, empty if none)
- Organization: Only if explicitly determinable (e.g. NVIDIA, Google, Meta)
- Hype tag: `[HYPE: X -> Y апвотов]` only for resurfaced papers
- No raw arXiv XML in output
- No duplicate papers in same digest
- **Terminology Education**: Use real ML/AI terminology with immediate Russian explanations in parentheses (e.g., 'KV-кэш (память модели о прочитанном тексту)') and include a glossary section for key terms

## Error Handling

- **arXiv API failure**: Log warning, continue with HF only
- **HF API failure (429)**: Fallback to individual paper API calls
- **Model timeout**: Retry with shorter prompt
- **No new papers**: Single line: «Новых статей и хайпящих повторов нет — сводка будет завтра»
- **Memory failure**: Reset seen.json and retry

## Rate Limits

- arXiv: ~1 request / 3 seconds (no API key)
- Hugging Face: 1 request / second (batch), fallback to 1/sec per paper
- Semantic Scholar: 1 request / second (for citation data, optional)

## Pitfalls

- **arXiv submittedDate lag**: Use 3-day window instead of relying on submittedDate field
- **HF rate limiting**: Individual paper API calls as robust fallback
- **False hype from 0→X**: Only count hype if previous upvotes were known (not 0 from API failure)
- **Organization overclaiming**: Only include organization if determinable from author affiliations
- **Replay protection**: Never reuse yesterday's digest if sources fail — output "no new papers" message
- **Race condition in manual testing**: When debugging, always use `--dry-run` flag to avoid marking papers as seen during manual script runs — manual runs with `--dry-run` do not update seen.json, preserving state for real cron runs

## Monitoring

- Check cron job status: `cronjob_manage --action list`
- View last run logs: check Telegram delivery
- Monitor seen.json growth: should stabilize around 300-500 papers
- Track HF API success rate: should be >90% with fallback

## Development

- Test with manual run: `python3 /root/.hermes/scripts/arxiv_digest_prefilter.py`
- Reset state: `echo '{}' > /root/.hermes/cron/arxiv_digest_seen.json`
- Debug individual paper fetch: `curl -s "https://huggingface.co/api/papers/{id}`"
- Verify arXiv categories: `curl -s "https://export.arxiv.org/api/query?search_query=cat:cs.AI&max_results=1"`

## Notable Features

- Smart deduplication with upvote tracking
- Hype-based resurfacing of trending papers
- Fallback mechanisms for API failures
- Compact author display with et al. handling
- Organization detection without overclaiming
- Replay protection on source failures
---

## References

- arXiv API: https://arxiv.org/help/api/user-manual
- Hugging Face Papers API: https://huggingface.co/docs/hub/api#papers
- Semantic Scholar API (optional): https://api.semanticscholar.org/
