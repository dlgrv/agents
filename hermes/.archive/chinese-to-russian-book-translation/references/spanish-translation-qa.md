# Spanish Translation Quality Assurance

## Purpose
This document provides specific QA techniques for Chinese-to-Spanish translation, addressing unique challenges that emerged during the HowToLiveBetter Spanish translation project (chapters 02–07).

## Spanish-specific QA issues

### 1. Number format preservation

**Issue:** Spanish subagents frequently translate numbers as words instead of digits, breaking byte-identity gates.

**Examples found:**
- `少 30 分钟` → `Treinta minutos` (should be `30 minutos`)
- `1990 年代` → `años noventa` (should be `años 1990`)

**Solution:** Always verify numeric preservation after Spanish translation:
```bash
# Check for word-form numbers that should be digits
grep -r "\b[Tt]reinta\|[Cc]iento\|[Mm]il\|[Vv]einti" /path/to/es/units/
# Replace with digit equivalents
sed -i 's/Treinta minutos/30 minutos/g' /path/to/es/units/*.md
sed -i 's/años noventa/años 1990/g' /path/to/es/units/*.md
```

**Rule:** All numeric values must match the source exactly — use digit form, not word form.

### 2. Source comment contamination

**Issue:** Spanish subagents insert Chinese cost tags (`<!-- 成本标签: ... -->`) directly into unit files, causing duplication during assembly.

**Solution:** Strip Chinese comments from unit files before assembly:
```bash
# Remove Chinese cost tags from all units
sed -i '/<!-- 成本标签:/d' /path/to/es/units/*.md
```

**Rule:** Chinese machine comments should only appear in source files, not in translation units.

### 3. Assembly verification

After assembling Spanish chapters, always run:
```bash
python3 tools/assemble_es.py <chapter> /path/to/units book/es/out-<chapter>.md
python3 tools/verify.py <chapter> --lang es --file book/es/out-<chapter>.md
```

**Success criteria:**
- `OK: headings=N tags=N sources=N numbers=N (lost=0, extra=M)`
- No `FAIL` or `numbers absent from translation` messages

### 4. Chapter integration

After QA passes:
1. Update README.es.md with correct Spanish slugs (kebab-case with accents)
2. Commit to `translation/es-w1` branch
3. Push to fork

## Spanish slug convention

Use kebab-case with preserved accents:
- `02-Não-Mueras-Lentamente.md` (not `02-Nao-Mueras-Lentamente.md`)
- `05-Inversión.md` (not `05-Inversion.md`)

## Verification checklist

- [ ] All numbers in digit form (not word form)
- [ ] No Chinese comments in unit files
- [ ] Assembly produces no duplication errors
- [ ] Verify script shows `lost=0` for all numeric values
- [ ] Chapter slugs use correct Spanish orthography
- [ ] Source lines byte-identical after field label conversion (`：`→`:`)
