# Upstream Sync Delta Handling

Workflow for detecting, mapping, and applying upstream content changes when the original repository recreates history or makes non-linear updates.

## Core Principle

**Never trust commit-based sync** — upstream may rewrite history (recreate branches, force-push, delete and recreate). Always compare content: `git diff main origin/main -- 'book/*.md'` (empty = CN base identical), count headings, validate glossary stats.

## Delta Detection Workflow

### 1. CN Base Verification
```bash
cd ~/github/HowToLiveBetter
git diff main origin/main -- 'book/*.md'  # Must be empty for CN sync
grep -c '^### ' book/*.md  # Count headings per chapter
grep -c '条术语/terms' README.*.md  # Glossary count consistency
```

### 2. Translation Impact Assessment
- If CN base unchanged → no translation work needed
- If CN changed → proceed with delta mapping

### 3. Delta Mapping Strategy

**Method:** Compare CN chapter texts using header diff (not commit diff):

```bash
cp book/*.md /tmp/zh_full/
for f in book/*.md; do
  bn=$(basename "$f" .md)
  diff <(grep '^### ' "$f") <(curl -s "https://raw.githubusercontent.com/eternity4719/HowToLiveBetter/main/book/$bn.md" | grep '^### ') > "/tmp/zh_delta/${bn#*-}.diff"
done
```

**Output:** `/tmp/zh_delta/NN.diff` files mapping:
- Added headers (`+ ### New Item`) → new units needed
- Removed headers (`- ### Old Item`) → units to remove
- Moved headers (`- ### X`, `+ ### Y`) → unit reassignment
- Content-only changes (no header change) → existing units need retranslation

### 4. Chapter Delta Analysis

**Per-chapter delta processing:**
- Parse `/tmp/zh_delta/NN.diff` for header changes
- Generate alignment map: `/tmp/align_final.json` mapping old→new unit numbers
- Example: ch01 adds 28/29, shifts old 28→30, 29→31, etc.

**Unit reassignment logic:**
- New units: translate from scratch
- Existing units: retranslate if content changed
- Removed units: delete from translation
- Migrated units: update content, keep translation

### 5. Fresh Digest Preparation

**Strategy:** Always use latest upstream digest:
```bash
cp -r tools/digest/<NN>/units /root/htlb-run-<lang>/<NN>/
# Overwrite old units with fresh CN source
```

**Why:** Digest contains latest CN structure and content; old units may be misaligned

### 6. Pilot Wave Planning

**Pilot chapters:** Always start with smallest (01) and largest (13) chapters:
- Validate full pipeline: digest → fresh units → translation → assemble → verify
- Test delta-specific issues: header shifts, content updates, field marker validation
- Measure volume: ch01=36 units, ch13=41 units, ch33=20 units

### 7. Translation Strategy for Deltas

**Full retranslate approach:**
- Translate ALL units in affected chapters (not just changed ones)
- Why: Content-only changes affect entire chapters, fingerprint matching unreliable
- Benefit: Consistent quality, no orphaned units

**Field marker validation:**
- RU: `Стоимость/Простыми словами/Эффект/Уровень доказательности/Примечания`
- EN: `Cost/In plain terms/Benefit/Evidence grade/Notes`
- ES: `Costo/En términos sencillos/Beneficio/Nivel de evidencia/Notas`
- Never use legacy labels (`Выгода`/`Ganancia`)

### 8. Verification Workflow

**Gates for delta work:**
- `tools/verify.py <NN> --lang ru|en|es` — structural and numeric validation
- `tools/assemble.py <NN> /root/htlb-run-<lang>/<NN>` — source injection
- Manual check: heading counts match CN, no orphaned units

**Common delta-specific issues:**
- Number format changes (comma vs dot, thousands separators)
- Field marker typos (legacy labels, wrong case)
- Missing units due to header shifts
- Extra units from misaligned counting

### 9. Quality Assurance for Deltas

**Parallel verification:** After translation wave, run verification subagents:
- Natural language flow check
- Field marker consistency
- Localization accuracy
- Numeric preservation

**Pilot validation:** Pilot wave must pass all gates before mass translation

### 10. Documentation and Reporting

**Delta report template:**
- Chapters affected
- Unit count changes (before/after)
- Translation volume estimate
- Quality gate results
- Next steps

## Pitfalls

- **Commit-based sync trap**: Never use `git log` or `git cherry` to detect changes — compare content directly
- **Fingerprint matching trap**: Never rely on unit fingerprint matching for deltas — content changes affect entire chapters
- **Digest staleness trap**: Always use fresh upstream digest, not cached local version
- **Header diff only**: Only compare headers (`^### `) for delta mapping — content diffs are too noisy
- **Legacy label trap**: Delta work often introduces old field labels (`Выгода`/`Ganancia`) — validate all markers
- **Number normalization trap**: Delta changes often alter number formats — normalize before comparison
- **Unit count mismatch**: Verify unit counts match CN exactly after delta mapping
- **CN-only changes**: Some delta changes only affect CN — verify RU/EN/ES unaffected

## Reference Scripts

- Delta mapping: `scripts/delta_mapping.py` (generates `/tmp/zh_delta/` and `/tmp/align_final.json`)
- Fresh digest copy: `scripts/fresh_digest_copy.py`
- Pilot wave validator: `scripts/pilot_wave_validator.py`
- Delta report generator: `scripts/delta_report_generator.py`

## Integration with Existing Pipeline

Delta handling is additive to existing HTLB translation workflow:
1. Detect delta using content comparison
2. Map changes and generate alignment
3. Prepare fresh digest units
4. Translate affected chapters (pilot first)
5. Verify with existing gates
6. Document and report

## Quality Gates for Delta Work

- **Structural integrity**: Unit counts match CN exactly
- **Field marker consistency**: No legacy labels, correct language-specific markers
- **Numeric preservation**: All numbers present and correctly formatted
- **Localization accuracy**: Chinese concepts properly adapted for target language
- **Web UI compatibility**: Capitalization rules applied for field values in index.html
