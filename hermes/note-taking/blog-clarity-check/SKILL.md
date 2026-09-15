---
name: blog-clarity-check
description: Use when writing a dlgrv.com blog post to audit its clarity.
---

# Blog clarity check (dlgrv.com)

Run AFTER drafting a section, BEFORE publishing. The unit of audit is one section (## heading to next ##), not the whole post.

## Source of principles

- **Distill.pub** (Clear, Dynamic, Vivid): every term gets an everyday analogy at first appearance; every number in the text is traced by the reader's eyes (no number accepted on faith); questions a reader would ask are pre-answered in the text.
- **Feynman test**: after each section there is a one-line anchor the reader could retell in their own words. If the reader cannot retell it, the section is not done.
- **Rhythm**: alternate dense and light paragraphs; no more than 2 dense paragraphs in a row; a section is not a wall of 7 uniform blocks.

## The checklist (run in this order)

### 1. Terms — first appearance must carry the definition

For every technical term in the section, find its first occurrence and check:

- [ ] Is the definition AT that occurrence (not several paragraphs later, not in a later section)?
- [ ] Is there an everyday analogy attached to the definition?
- [ ] Is the term ever used BEFORE its definition? (= bug, fix by moving definition earlier or rewording the early mention)
- [ ] English terms in parentheses (residual stream, weight tying…) — either give them an analogy next to them, or cut them. A bare latin term in brackets is noise.

### 2. Numbers — traced, not stated

- [ ] Every number is either computed in front of the reader (chain of values) or illustrated with a concrete example.
- [ ] No number appears that the reader must accept on faith.

### 3. Pre-answered questions

For each new concept, write down the 2-3 questions a reader would ask (what is it? why does it exist? how does it physically work?). Each must be answered in the same section, explicitly.

### 4. Connections between mechanisms

- [ ] If section says «X does Y», the physical mechanism of Y is shown (e.g. «layer writes understanding into vector» → show that vector coordinates = neuron outputs).
- [ ] No gap of the form «mechanism A described, consequence B claimed, link missing».

### 5. Anchor + rhythm

- [ ] Section ends with a one-line Feynman anchor: a sentence the reader could retell. Often phrased as «Если можешь пересказать: … — листай дальше».
- [ ] No more than 2 dense paragraphs in a row; split overloaded paragraphs (max 1-2 ideas each).
- [ ] Each paragraph starts by picking up a word from the previous one (rhythm), not by abruptly switching topic.

## Report format

```
CLARITY AUDIT — <section name>
Terms: ✅/⚠️/❌ per term (term — verdict — quote)
Numbers: ✅/⚠️/❌
Pre-answered questions: list of unanswered ones
Connections: list of missing links
Anchor: ❌ missing / ✅ present
Rhythm: verdict
→ rewrite / minor fixes / clean
```

## Rewrite rules

- Fix deepest layer first: connections (4) → terms (1) → anchor/rhythm (5).
- Keep the author's voice: first person, metaphors already present stay.
- Do not add new sections — work inside the audited one.
- After rewriting, re-run the checklist once; if any ❌ remains, iterate.

## Example finding (from a real audit)

Step «Скрытые слои» had: «слой дописывает понимание в черновик» — but the physical link (vector coordinates = neuron outputs, 4096 numbers = 4096 neurons) was missing. Fix: one paragraph «каждое число вектора — выход одного нейрона; слой — 4096 нейронов; поэтому ширина = количество нейронов».