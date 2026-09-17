# TRANSLATION.md — Chinese-to-Russian translation conventions

## Byte-faithful elements (never translate)
- All numbers and statistics (HR/RR/OR/CI, 498, 323/126/49, 891, 88/248/162, 97.2%, 20–48%, 38,227)
- DOIs and URLs
- Machine-readable tag comments (<!-- 成本标签: 钱=0 时间=少 毅力=些 收益=大 口径=死亡率 -->)
- Field labels (来源→Источники, 成本→Затраты, 收益→Выгода, 证据等级→Уровень доказательности, 备注→Примечания)

## Field-label translation
- 来源 → Источники
- 成本标签 → Затраты/Выгода/Риск (in comments)
- 收益 → Выгода
- 证据等级 → Уровень доказательности
- 备注 → Примечания

## File naming convention
- Use Russian slugs: `01-Не-умирайте-рано.md`, `02-Не-умирайте-медленно.md`
- Document in TRANSLATION.md: `book/ru/` filenames use Russian slugs, not Chinese

## Per-file header template
```markdown
> Неофициальный перевод файла [../<original-chinese>.md](../<original-chinese>.md). При расхождениях приоритет у китайского оригинала.

[← К общему оглавлению](../../README.ru.md)

# <Russian Title>

<Optional disclaimer about Chinese-specific context/laws>
```

## Localization rules
- Replace Chinese jargon with natural Russian equivalents (e.g., «когорта» → «группа»)
- Adapt phrasing to Russian idioms, avoid calques
- For Chinese legal/administrative terms, provide Russian translation + original in parentheses at first mention
- Preserve all numbers, statistics, and structure byte-faithful

## Verification checklist
- item counts match source
- tag-comment counts match source
- DOI counts match source
- sources are byte-faithful after label translation
- zero untranslated han outside allowed zones (links, parentheses)
- all back-links use correct relative path to README.ru.md