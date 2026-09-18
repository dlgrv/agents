---
name: blog-article
description: Use when Leonid asks for a dlgrv.com blog post.
---

# Blog article workflow (dlgrv.com)

Validated end-to-end on logistic-regression (2026-09-18, PR #126). One lesson = one article; only lessons Leonid has completed (зелёные галочки в Coursera).

## Pipeline

1. **Scope check FIRST**: read the previous article's ending — it promises the next topic; diff against what's already covered to avoid overlap. Confirm scope with Leonid if ambiguous.
2. **Recalculate every number honestly in Python BEFORE writing** (sigmoid values, chain example, descent steps, boundary points). Keep ONE numeric example consistent across the series: x=[0.5,0.3,0.9], w=[1.2,-0.4,2.0], b=-0.9, y=1, α=0.1.
3. **Figures**: matplotlib, grayscale only (INK #111, MUTED #666, FAINT #e3e3e3), serif DejaVu, savefig bbox=tight pad=0.15, SVG+PNG(dpi=192) per figure into public/blog/<slug>/. Programmatically assert geometry (e.g. all cat points z>0, non-cat z<0) — vision review catches violations but times out often. mathtext breaks inside bash heredocs — write the python script to a file first.
4. **Write index.md**: intro linking the previous article, Оглавление with {#anchors}, sections ending with «Если можешь пересказать: …, — листай дальше», «Что дальше» bridging to the next lesson. Formulas in $...$ / $$...$$ (Temml → MathML). No Coursera/«неделя»/«Ын» mentions inside the article text.
5. **Numeric audit**: re-check EVERY number against printed text. Print 4 digits of ŷ in tables so L = −log(ŷ) verifies from printed values (rounding mismatch = reader confusion). Probability is «N из 10», never «N к 1» (odds ≠ probability).
6. **Two parallel subagent reviews**: (a) math — recalculates every claim with Python; (b) editor — structure/style/render vs previous articles. Both found real issues in the pilot (odds mistake, rounding chain, anaphora, promise contradiction). Fix all blocking, re-audit, re-render.
7. **Ship**: npm run build:pages → check-math-in-code-spans → blog-renderer vitest → commit to feat branch → PR → squash-merge → verify prod by CONTENT (blog/index.json has slug, article/figures return 200).

## Traps

- Whole-repo `npm run check` fails on this machine (Node 26 vs jsdom, ~37 test files) even on clean main — run targeted tests: blog-renderer spec + check:math. Don't fix unrelated env failures.
- index.json and sitemap.xml are hand-edited; build:pages does NOT regenerate index.json.
- PR body via GitHub MCP: \r\n in JSON; read back for stray backslashes (\5 leaked into #126 body).
- matplotlib/numpy: installed with pip3 --break-system-packages on 2026-09-18; hermes venv doesn't have them.

## Not yet written
- Векторизация (promised at the end of both binary-classification and logistic-regression).

## Published articles (style reference, public/blog/<slug>/index.md)
- how-llm-works (2026-09-08) · binary-classification (2026-09-13) · logistic-regression (2026-09-18)