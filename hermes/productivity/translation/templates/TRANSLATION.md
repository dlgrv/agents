# Translation conventions — starter (copy into fork root as TRANSLATION.md, adapt)

## Status line — FIRST line of every translated file, before the back-link

> Unofficial translation of [book/<original>.md](../<original>.md). In case of any discrepancy the <source-language> original prevails.

(Adjust the relative path for the translated file's depth: from `book/en/` or `book/ru/` the source is `../<original>.md`, the root README is `../../README.md`.)

## Byte-faithful — translate NOTHING inside these

- Citation/source lines (e.g. `- 来源：…`): only the field label translates; the rest of the line stays byte-identical — author names, journal names, DOIs, URLs, regulation titles + document numbers, embedded quotes (even when the quote is in the source language).
- Machine tags: `<!-- 成本标签: ... -->` and any other machine-readable comments, verbatim.
- All numbers, units, ranges, confidence intervals, p-values.
- Code, identifiers, link targets (except relative depth, which must be re-adjusted), filenames in visible link text.

## Field-label mapping

| Source | EN | RU |
|---|---|---|
| 来源 | Sources | Источники |
| 成本 | Cost | Затраты |
| 收益 | Benefit | Выгода |
| 证据等级 | Evidence grade | Уровень доказательности |
| 备注 | Notes | Примечания |

(extend per project)

## Body-text rules

- Numbers, statistics (HR/RR/OR/CI), grade letters (A/B/C) pass through unchanged.
- Titles verb-first; restrained tone; no exclamation marks; no moralizing.
- Quotes that the original itself rendered in the source language (e.g. an English paper quote rendered in Chinese) are translated INTO the target language meaning-wise — the original wording lives in the byte-faithful citation line.
- Country-specific facts and institutions are translated faithfully, never localized; chapters citing the source country's law get one line under the heading: "Chapter N cites <country> laws and institutions; for readers outside <country> it is reference material, not applicable law."

## Verification gate (main agent, scripted)

count(### items) and count(tag comments) and count(doi.org lines) in the translation == the source's actual counts (grep the source, don't trust stated counts); no source-language text outside the byte-faithful zones.
