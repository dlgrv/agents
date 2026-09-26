---
name: htlb-plainness-gate
description: Use when checking or enforcing translation plainness.
---

# HTLB Plainness Gate

North Star: перевод должен быть безумно понятным для носителя — очень простой и понятный язык, чтобы всё безумно легко читалось.

## Tools

### 1. Bureaucratese Checker (`tools/bureaucratese.py`)

Flags канцелярит — bureaucratic language that makes text harder to read.

```bash
# Check a language directory
python3 tools/bureaucratese.py ru
python3 tools/bureaucratese.py en
python3 tools/bureaucratese.py es

# JSON output for automated processing
python3 tools/bureaucratese.py ru --json
```

Exit codes: 0 = clean, 1 = violations found.

RU patterns checked: nominalisations (производить анализ), genitive chains (4+), passive voice (является сделан), formal connectors (в соответствии с), demonstrative pronouns (данный).

### 2. Readability Scorer (`tools/readability.py`)

Flesch-Kincaid adapted for RU/EN/ES.

```bash
# Score all chapters in a language
python3 tools/readability.py ru
python3 tools/readability.py ru --desc  # hardest first
python3 tools/readability.py ru --json
```

Target: score ≥ 60 (легко / easy / fácil). Below 60 = needs simplification.

Scale for RU:
- 80-100: очень легко (5 класс)
- 60-79: легко (7 класс)
- 40-59: средне (9 класс)
- 20-39: сложно (студент)
- 0-19: очень сложно (специалист)

## Quality Gates

Plainness gates run ADVISORY (WARN), not blocking (FAIL):

1. `bureaucratese.py` — flags patterns; translator reviews and simplifies
2. `readability.py` — measures score; chapters below 60 get a simplify pass
3. Neighbor test (manual) — would a teenager without specialist training understand it?

## Integration

Add to `make ci` or pre-commit checks:

```makefile
plainness:  ## Readability + bureaucratese audit
	python3 tools/readability.py ru
	python3 tools/bureaucratese.py ru
```

## Pitfalls

- Bureaucratese checker has false positives — review flagged patterns before editing
- Readability scores are heuristic; a score of 58 vs 60 is not meaningful
- Legal/medical chapters naturally score lower; the target is direction, not absolute
- Never simplify at the cost of accuracy — fact-check (pass E) comes before plainness
