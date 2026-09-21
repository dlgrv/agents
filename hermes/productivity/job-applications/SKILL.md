---
name: job-applications
description: Use when writing hh.ru cover letters or screening replies.
---

# Job applications (hh.ru and similar)

Deliverables to the user are in Russian. Hard rule: never fabricate experience or stack. AI filters screen the letter, but interviewers verify claims downstream — an invented project converts to rejection more reliably than an admitted gap, and a confident wrong fact is itself a top detector tell.

## Workflow

1. **Extract the vacancy, don't recall it.** hh.ru vacancy pages embed the full description as JSON-LD (`<script type="application/ld+json">`, field `description`, HTML inside). Fetch the page and parse that block; rendered-text scrapes lose structure. Record two things that dictate letter content: the "В отклике" block (what the employer asks applicants to include) and any "!Отклики фильтрует встроенный ИИ" warning (keyword matching is active).
2. **Source the user's real experience from artifacts.** Verified facts live at dlgrv.com/cv and in the hh.ru resume itself — fetch and use those; do not write claims from memory of past sessions.
3. **Map real experience to the vacancy's keywords, including "будет плюсом" items.** Rare domain matches (e.g. AdTech/oRTB for a DSP role) go in as their own prominent section — they differentiate more than generic stack lists. Mirror the vacancy's scenario vocabulary (metric names, subsystem names) so keyword filters hit.
4. **Honest-gap strategy for a missing requirement** (e.g. the vacancy's primary language is not the user's primary): order sections strongest-first —
   - open by covering the requirements that ARE native ("half your stack is native: Go + Python"),
   - then the strongest unique production match,
   - then rare domain,
   - then the gap in ONE short clause + a concrete proof offer ("готов подтвердить тестовым заданием"). Frame transferable practice specifically (typing, async, DI, schema validation), never "быстро обучаюсь".
   - Never end the letter on the weak point; the proof offer converts the gap into an action item.
5. **Replies to hh AI-assistant screening questions:** same strategy, shorter. Match the question's checklist order where possible, stay honest about gaps, end with the test-task offer. Do not pad — the assistant counts minutes, not words.
6. **Length:** cover letter ~1500–2500 chars; one screening-question reply is shorter than that.
7. **Sepia pass before delivery.** The user expects a /sepia (refactor) pass on final application text. This genre's recurring defects: every bullet built on one "Term: proof" frame (templatedness), a frame phrase repeated across bullets, rule-of-three clusters in adjacent bullets, uniform bullet lengths. Fix by replace/delete; keep every fact.

## Pitfalls

- Don't overclaim to beat the AI filter — the filter is pass-through; the interview is the real gate, and fabrication fails there retroactively.
- Don't restate the vacancy back at the employer ("вы ищете…") — letters that parrot the description read as templated to both the filter and the recruiter; use its vocabulary inside claims about the candidate instead.
