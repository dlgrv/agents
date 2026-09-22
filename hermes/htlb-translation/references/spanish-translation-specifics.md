# Spanish Translation Specifics

## Field Markers (CN→ES)

| Chinese | Spanish | Notes |
|---------|--------|-------|
| 成本 | Costo | Cost/expense field |
| 说人话 | En términos sencillos | Simple language field |
| 收益 | Beneficio | Benefit/effect field |
| 证据等级 | Nivel de evidencia | Evidence level (A/B/C remain) |
| 备注 | Notas | Notes/remarks field |

## Spanish-Specific Rules

- **Number formatting**: Use space thousands separator, decimal comma (e.g., 248 099, 17,4)
- **万/亿 conversion**: 万 → ×10 000, 亿 → ×10⁸, written out as 'miles'/'millones' with correct magnitude
- **Capitalization**: Field values (Costo, En términos sencillos, Beneficio, etc.) get first letter capitalization in web UI only
- **Legal terms**: Keep Chinese hanzi + short Spanish gloss on first use (e.g., 《民法典》 (Código Civil))
- **Units**: 元 → yuanes; keep mmHg, mg, %, °C as-is
- **Emergency numbers**: Add localization in parentheses: 'llame 120 (para China — 112/103, para España — 112)'

## Critical Pitfalls from Wave 1

- **Never insert `<!-- 成本标签 ... -->` comment lines into units** — the assembler injects them via §TAG§; a hand-inserted copy breaks the gate and causes duplication (40 instead of 20 comments in ch03).
- **Never write numbers as words** («Treinta» → «30», «años noventa» → «años 1990») — always use digits with Spanish formatting (80 300, 17,4).
- **Never round or invent digits** — 8.03 万 = exactly 80 300, never '80 300' rounded to '80 000'.

## Assembly and Verification

- **Assembly script**: `tools/assemble_es.py` (injects sources, validates unit count, generates out-NN.md files)
- **Verification script**: `tools/verify.py <NN> --lang es` (same rules as RU, handles Spanish-specific false positives)
- **Status line**: Add to chapter 00.md: `> Unofficial translation of [book/NN-*.md](../NN-*.md). In case of any discrepancy the Chinese original prevails.`
- **Back-links**: Use `[← Volver al índice](../../README.md)` in Spanish chapters (relative to book/es/)

## Web UI Integration

- **README.es.md**: Create with language selector (`**Idiomas / Languages:** [中文](README.md) · [Русский](README.ru.md) · [Español](README.es.md)`) and chapter links to Spanish slugs
- **Capitalization rules**: Apply to web UI chip labels and field values (first letter only) for Spanish interface
- **Field labels**: Must be exactly `- Costo:`, `- En términos sencillos:`, `- Beneficio:`, `- Nivel de evidencia:`, `- Notas:`

## Chapter Structure

```markdown
# 2. No te dejes morir lentamente

[← Volver al índice](../../README.md)

> Unofficial translation of [book/02-不要慢慢死.md](../02-不要慢慢死.md). In case of any discrepancy the Chinese original prevails.

### 1. Dejar de fumar, cuanto antes mejor

- Costo: 0 yuanes; dejar de fumar es gratis
- En términos sencillos: si fumas, cada cigarrillo daña tu salud
- Beneficio: reducción del riesgo de cáncer en 30-50%
- Nivel de evidencia: A
- Notas: basado en estudios de cohorte

§TAG§
§SRC§
```