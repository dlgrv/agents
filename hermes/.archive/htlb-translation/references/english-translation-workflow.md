# English Translation Workflow (HTLB)

## Pilot Wave Setup

1. **Prepare EN slugs table** in TRANSLATION.md before starting translation
   - Two-digit prefix + English title slug (e.g., `01-Do-Not-Die-Early.md`)
   - Record all 31 chapters in naming table
   - Commit to `translation/en` branch

2. **Adapt assembly script** for EN field labels
   - Sources: `- Sources:` (not `- Источники:`)
   - Evidence grade: `- Evidence grade:` (not `- Уровень доказательности:`)
   - Use `tools/assemble_en.py` (copy of assemble.py with EN labels)

3. **Prepare run directories** for pilot chapters
   - Copy digest units to `/root/htlb-run-en/<chapter>/units/`
   - Ensure unit count matches digest metadata

## Pilot Wave Execution

1. **Dispatch subagents** for chapters 01 and 13
   - Each subagent gets one chapter (not unit)
   - Strict instruction: write files immediately, no analysis
   - Include EN field label mapping and conventions in task
   - Pilot tests: digest, assembly, web UI capitalization, EN field labels

2. **Assemble and validate** after translation
   ```bash
   python3 tools/assemble_en.py <chapter> /root/htlb-run-en/<chapter> /tmp/output.md
   ```
   - Check byte-identical sources
   - Verify field labels are correct
   - Count items/tags/sources match

3. **Commit pilot chapters**
   - One chapter per commit
   - Message: `translation(en): chapter <chapter>`
   - Push to `translation/en` branch

## Wave Planning

| Wave | Chapters | Total Units |
|------|----------|-------------|
| Pilot | 01, 13 | 71 |
| 1 | 02-06 | 112 |
| 2 | 07-11 | 105 |
| 3 | 12, 14-17 | 41 |
| 4 | 18-22 | 60 |
| 5 | 23-27 | 62 |
| 6 | 28-31 | 79 |

## English Translation Conventions

### Field Labels
- 成本 → `- Cost:`
- 说人话 → `- In plain terms:`
- 收益 → `- Benefit:`
- 证据等级 → `- Evidence grade:` (A/B/C unchanged)
- 备注 → `- Notes:`
- Sources line: leave `§SRC§` placeholder (injected mechanically)

### Localization Rules
- **Numbers**: Copy byte-for-byte; 万 → numeric conversion (2 万 = "20,000 yuan")
- **Chinese law/regulation titles**: Not translated; refer descriptively in body
- **China-specific concepts**: First use: transliteration + gloss (e.g., "dibao (低保 — means-tested minimum subsistence allowance)")
- **Item titles**: Start with a verb
- **Style**: No exclamation marks, restrained tone
- **"In plain terms"**: Natural spoken English, never calque, no numbers absent from Benefit line
- **Status lines**: Translate visible text, keep link targets byte-identical

### Quality Assurance
- **Unit-based QA**: Slice into ~10-line pairs for parallel verification subagents
- **Verification**: Check byte-identical sources, field labels, no Chinese characters in visible text
- **Wave validation**: After each wave, verify counts and structure match source

### Git and PR Workflow
- **Branch**: `translation/en`
- **Commit**: One chapter per commit, clear messages
- **Fork main merge**: Only after complete translation, merge `translation/en` → `main`
- **GitHub Pages**: Enable in fork for live reading at `dlgrv.github.io/HowToLiveBetter/`
- **Issue management**: Issue title in Chinese, body in Chinese with brief EN note

### Common Pitfalls
- **Never let subagents spend time on analysis** — must write files immediately
- **Preserve placeholders**: Leave `§TAG§` and `§SRC§` untouched in unit files
- **Field label consistency**: Use exact EN labels, not Russian equivalents
- **Emergency numbers**: Keep Chinese numbers in item text, add localization notes
- **Legal identifiers**: Preserve byte-for-byte, refer descriptively in body
