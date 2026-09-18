# Chinese-to-English Translation Extension

This workflow extends the core Chinese-to-Russian translation process for HowToLiveBetter English translation, incorporating lessons from the pilot project (chapters 01 and 13).

## Prompt Engineering

- **Strict 'one unit per step' loop:** Each translation subagent must read one unit file, translate it, and immediately write the translated file to the same path.
- **First tool call = write_file:** The very first action in each subagent must be a `write_file` of the translated unit (e.g., translate and write 00.md first). This prevents burnout on reasoning without output.
- **Inline conventions:** Embed ALL translation rules directly in the prompt — never reference external files like TRANSLATION.md. Include:
  - Field mappings: 成本→`- Cost:`, 说人话→`- In plain terms:`, 收益→`- Benefit:`, 证据等级→`- Evidence grade:`, 备注→`- Notes:`
  - Byte-faithful requirements: Numbers/prices/HR/RR/OR/CI must be identical
  - 万 → numeric conversion (2 万 = 20,000)
  - China-specific terms: transliteration + gloss (e.g., "dibao (低保 — means-tested subsistance allowance)")
  - No invented facts/numbers, no exclamation marks, restrained tone
  - Item titles start with verb
  - Status line/back-link visible text translated; link targets byte-identical

## Chapter Organization

- **Unit slicing:** Use `make_digest.py` to slice chapters into 1-2 KB units
- **English slug convention:** Use kebab-case filenames (e.g., `13-Emergencies.md`)
- **Unit count verification:** Actual unit counts may differ from stated counts — verify with `ls units/*.md | wc -l`

## Parallel Processing

- **Wave dispatch:** Launch chapters in batches (e.g., 5 chapters per batch) with identical prompts
- **Concurrent monitoring:** Use a watchdog cron job to monitor delegation logs every 3 minutes
- **Status tracking:** Maintain running tally of completed chapters and active waves

## Quality Assurance

### Automated verification after assembly

- **Heading count:** Must match source exactly
- **Item count:** Must match source exactly  
- **Tag-comment count:** Must match source exactly
- **DOI-line count:** Must match source exactly
- **Source line byte-identity:** After stripping field labels (source uses `：`, translation uses `:`)
- **CJK check:** Zero CJK outside allowed zones (allowed: link targets, §TAG§/§SRC§ placeholders)

### Common issues to catch
- **Model timeout:** Long chapters may timeout (e.g., ch13 took 3 attempts). Retry with identical prompt + shorter timeout (1000s)
- **CJK contamination:** Only byte-identical link targets are permitted (e.g., `../docs/遇到陌生人出事该不该停.md`)
- **Invented facts:** Watch for added numbers or claims not in source
- **Punctuation errors:** Replace Chinese punctuation with English equivalents

## Commit Strategy

- **One commit per chapter:** Descriptive message including verification status
- **Verification in commit message:** e.g., "tags/sources byte-identical"
- **Branch strategy:** Work in `translation/en` branch, push to fork (no PR to upstream per author request)

## Watchdog Automation

- **Cron monitoring:** Run every 3 minutes to check delegation logs
- **Alert conditions:** Notify if any subagent stalls for ≥6 minutes
- **Log paths:** Monitor `~/.hermes/cache/delegation/live/deleg_*/task-*.log`
- **State tracking:** Persist completion status between runs

## Recovery Procedures

- **Subagent failure:** Recover from cache transcripts under `~/.hermes/cache/delegation/`
- **Timeout retry:** Use identical prompt with reduced timeout (1000s)
- **Verification failure:** Re-run assembly script and re-verify counts

## Progress Tracking

- **Running tally:** Track completed chapters (e.g., "2/31 chapters complete")
- **Wave monitoring:** Use delegate_task status queries to monitor active batches
- **MR updates:** Keep translation MR updated with current progress
