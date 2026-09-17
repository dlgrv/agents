# Chinese-to-Russian translation best practices (localization & navigation)

## Key localization rules
- Replace Chinese jargon with natural Russian equivalents (e.g., «когорта» → «группа» or «контрольная группа»)
- Adapt phrasing to Russian idioms, avoid calques
- Use Russian slugs for filenames (e.g., `不要早死` → `01-Не-умирайте-рано.md`)
- Preserve all numbers, statistics, and structure byte-faithful

## Navigation consistency
- In all `book/ru/` files: `[← К общему оглавлению](../../README.ru.md)`
- Adjust relative path depth if README.ru.md is nested
- Chinese source files stay byte-identical (never alter upstream)

## README.ru.md structure
- Status line: `> Неофициальный перевод файла [README.md](README.md). При расхождениях приоритет у китайского оригинала.`
- Language selector: `**Языки / Languages:** [中文](README.md) · [Русский](README.ru.md)`
- All numbers/statistics byte-faithful (498, 323/126/49, 88/248/162…)
- Chapter links → `book/ru/<russian-slug>.md`
- Badges with Russian labels (URL-encode programmatically)
- Anchors to translated headings (#Оглавление, #Как-читать, etc.)

## Chinese-specific terminology
- For Chinese legal/administrative terms (e.g., 认缴出资, 一裁终局), provide Russian translation + original in parentheses at first mention
- Example: «认缴出资 (зарегистрированный капитал)»

## Verification checklist
- item/heading counts match source exactly
- tag-comment counts match source
- doi.org-line counts match source
- zero untranslated text outside byte-faithful zones
- all back-links use correct relative path
