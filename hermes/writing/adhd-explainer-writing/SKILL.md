---
name: adhd-explainer-writing
description: Use when writing math/ML explainers for ADHD readers.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [writing, adhd, education, ml-notes]
    related_skills: [blog-article]
---

# Writing explainers for ADHD readers

## When to use

- Writing or editing any explanatory math/ML article (course notes, blog explainers) whose audience includes ADHD readers or must satisfy the user's «объясни пятилетке» bar.
- Reviewing such articles before publishing — use the three-persona review panel below.
- Delegating article rewrites or reviews to subagents.

Class-level rules for any explanatory article (course notes, blog explainers) that must hold attention of a reader with ADHD and satisfy the user's «статья должна быть понятна даже 5-летнему ребёнку» bar. Intuition and «зачем это мне» must survive; formulas are the adult version of the same idea, never the entry point.

## Always-on rules

- Life analogy BEFORE the formula for every new concept. A bare formula followed by an apology is a fail; the analogy IS the explanation.
- One plain-words reminder per symbol at first use, inline («ŷ — предсказание модели, число от 0 до 1»). Never dump 2-3 new symbols in one sentence.
- The «зачем это мне» hook goes at the START of the article, not the end. If the only practical motivation sits in the last paragraph, the ADHD reader never reaches it.
- Numeric examples show at least one intermediate calculation step, not just final numbers — final-only numbers force the reader to trust or re-derive.
- One thought per paragraph. A sentence doing 3+ distinct jobs gets split. Dense parallel number lists become tables (example / вклад A / вклад B).
- Re-anchor every 2-3 paragraphs in long calculation blocks: a checkpoint («Если можешь пересказать — листай дальше»), a mini-«смотри: …» observation, or an anchor sentence. Checkpoints only at section ends are too rare.
- One consistent metaphor system across the whole series — cross-article consistency beats variety; see references/adhd-metaphor-system.md for the approved table.
- Short reference articles stay short: analogy + numbers + pointer to the full article. Adding explanations must not bloat them into derivations.
- Recompute every numeric claim in Python before publishing; a single wrong averaged value undermines trust in everything else. Prose reviewers miss arithmetic errors — a dedicated fact-checker pass is mandatory, not optional.

## Review panel (parallel delegation fan-out)

Three personas, dispatched in parallel, each reading the full article(s):

1. **ADHD reader** — where the thread is lost (exact paragraph), whether hooks re-anchor often enough, score 1-10 on «запомнит ли смысл через неделю» (NOT «понял ли формулу»).
2. **Metaphor auditor** — reads ALL articles at once, lists every concept introduced without an everyday analogy, proposes one from the shared metaphor table, enforces consistency.
3. **Numeric fact-checker** — extracts every computed value and recomputes in Python via terminal; reports claimed vs recomputed with likely cause.

Pitfall: review subagents sometimes stop mid-reasoning and emit no final review. Re-dispatch with an explicit «Output ONLY the finished review, no reasoning trace» in the goal — this reliably completes them.

When editing from review findings, edit in the PR-branch worktree, never a throwaway preview worktree — preview edits are lost at merge.

## References

- references/adhd-metaphor-system.md — approved metaphor table, evidence-based ADHD engagement techniques, ready-to-paste reviewer brief template.
