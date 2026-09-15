# Design Reference Benchmarking — N references vs current app UI

Worked example + method from a real audit: user's license-service личный кабинет (ЛК) was criticized by stakeholders ("разные шрифты", "ужасная типографика", "слишком просто, как 2010", "мелкие непонятные шрифты"). Design reviewer pre-approved 4 v0.app templates. Task: compare all 4 against the current app and recommend a direction.

## Method (validated end-to-end)

### 1. Audit the current app from CODE first
Before touching references, inventory what the app already has — this is what makes the final recommendation adoptable without new assets:
- Read the theme/token file (`packages/shared/src/shared/config/styles.css`): loaded `@font-face` files, `--*-font`, `--*-font-mono`, background/wash tokens.
- Grep usage patterns to see how tokens are actually used:
  ```bash
  grep -rhoE 'text-(xs|sm|base|lg|xl)\b' src/pages src/widgets | sort | uniq -c
  grep -rl 'font-mono' src/pages src/widgets        # e.g. mono used in ONE table cell only
  grep -rhoE 'text-\[[^]]+\]' src | sort | uniq -c   # arbitrary sizes
  ```
- Screenshot the current UI if shots exist in the repo (often under a `design-review/` folder).

Key insight this produced: the app already shipped Inter + a brand mono font, but the mono was used in exactly one place — so "разные шрифты" was fixable by *adopting* the existing pairing system-wide, not by adding fonts.

### 2. Extract the references
For **v0.app templates** (`https://v0.app/templates/<slug>`):
- Browser/CDP may be blocked ("Allow remote debugging" popup — see curl fallback in SKILL.md). Don't stall: `curl -sL` each template page, pull the official screenshot / og-image URLs out of the HTML, download them.
- Template page → screenshot → `vision_analyze` is enough for a style verdict. Live-preview DOM extraction is nicer (exact hex) but usually not required to choose a direction.
- Watch out: the 4th template's first screenshot hit was the showcase of a *different* template — verify each screenshot actually shows the named template (check logo/title in the image) before analyzing.

### 3. Vision-analyze everything (downscaled)
Analyze each reference screenshot AND the current-app screenshot with the same question template (palette, typography, cards/effects, density, weaknesses) so the comparison is apples-to-apples. Downscale first — see pitfall below.

### 4. Compare on fixed dimensions
Table rows: theme · palette (hex) · typography pairing · card/effect language · density · character. Then judge **fit-for-purpose, not taste**:
- A gorgeous reference can be wrong for the domain (calendar-editorial grid with giant display dates does not fit a finance/licenses dashboard).
- A functional reference can still be the wrong *style* (a clean financial dashboard template that is exactly as neutral as the UI being criticized — adopting it re-imports the complaint).

### 5. Recommend a hybrid mapped onto EXISTING tokens
The persuasive structure that worked:
1. Base system = the reference with the most character whose architecture fixes the actual complaints (its two-font system: display + mono-labels maps 1:1 onto fonts the codebase already ships).
2. Named borrowings: card composition from one template, status-color language from another, one principle from a third.
3. Map everything to existing tokens (`--pp-wash-*` gradient = the colorful underlay glass needs; brand mono = label/number font).
4. Effect recipes with do/don't (see glassmorphism below).
5. Close by offering mockup-before-code (the `sketch` skill) — this user's standing rule is options-before-code.

## Glassmorphism recipe (dark app, validated reasoning)
Requires a colorful underlay — flat dark gray gives blur nothing to diffuse. Gradient/wash tokens are ideal.
```css
card {
  background: color-mix(in srgb, var(--pp-wash-base) 55%, transparent);
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%); /* Safari */
  border: 1px solid rgb(255 255 255 / 8%);
}
```
- Apply to: dashboard cards, sidebar, sticky topbar, modals, dropdowns.
- Do NOT apply to: data tables and dense forms (blur under text = mud), and never glass-on-glass.
- Add `@supports not (backdrop-filter: blur(1px))` opaque fallback.
- Perf: expensive on large areas; don't put it on whole scroll containers.
- Raise text opacity to 90–95% on glass — low-contrast text on glass multiplies the exact complaint being fixed.

## Report structure
Comparison table → per-reference adopt/reject rationale (one line each) → hybrid recommendation with reasons tied to each stakeholder complaint → where-not-to-apply notes → offer of mockup. State the method honestly: if live extraction failed and official screenshots were used, say so.
