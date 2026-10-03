---
name: ml-bio-papers
description: "Use for ml-bio-papers repo work: translations, fixes, site."
---

# ml-bio-papers

Russian translations of metagenomics papers. Pipeline details live in the repo's TRANSLATION.md — read it first. One paper = `papers/<slug>/` (published: `index.md`, `index.pdf`, `meta.yml`); work dir `translate/runs/<slug>/` is gitignored.

## Rules

- No repair step: when units fail validation, fix the unit YAMLs by hand (`python -m translate.steps.fix.fix_unit <slug> <uid> <new-text>`). Re-running the model on units it already stumbled on yields nothing and wastes the wait.
- Site look is 1:1 with dlgrv.com notes: `site-assets/pages.css` is a byte-identical copy of `~/github/dlgrv.com/public/static/pages.css` (verify with `diff` after re-copying). Never add font/size/margin overrides for article content — the user reverts them; the only sanctioned extra is the stretched-link rule for `.blog-index a.paper-link`.
- A paper appears on the site only when its `meta.yml` status is not `not-started`.

## Site

- Build: `.venv/bin/python -m translate.steps.site.build_site` → `site/` (list page + `<slug>/`, `.nojekyll`, MathML via pandoc `--math-method=mathml`, `--shift-heading-level-by=1` because bodies start at h2, h3-based TOC). Tests: `translate/validate/tests/test_build_site.py`; gates `make lint && make test`.
- Preview under the deploy path prefix: symlink `site` into a temp dir as `ml-bio-papers/` and serve the parent with `python3 -m http.server`. Serving at `/` hides relative-URL breakage that shows up on dlgrv.github.io/ml-bio-papers/.
- Deploy NOT yet wired: no `.github/workflows`, Pages off in repo settings; `site/` is gitignored for now.

## PDF

PDF goes through pandoc with the Typst engine. weasyprint does not render MathML — formulas come out as raw markup text.
