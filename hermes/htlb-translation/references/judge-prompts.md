# Judge prompts (pointer)

Canonical judge prompt templates live IN THE REPO (versioned, prompt_hash
is computed from them by tools/pipeline/store.py):

- `tools/prompts/judge-screen.md` — source-blind fluency screen (verdict: native|translationese|broken)
- `tools/prompts/judge-ab.md` — A/B pairwise escalation (winner: 1|2|tie)
- `tools/prompts/judge-factcheck.md` — pass E factcheck, CN-span-grounded
  (taxonomy: dropped_condition, reversed_logic, softened_claim, added_advice,
  subject_swapped, cross_unit_contradiction, invented, other)

Do not edit copies here — edit the repo files; this reference is a pointer only.
Judge model: GLM-5.3-Flash via z.ai (Hermes subagents primary; direct HTTP fallback
via tools/validate/judge.py with ZAI_API_KEY).
