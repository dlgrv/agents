---
name: htlb-repo-init
description: Use when initializing a fresh HTLB translation clone.
---

# HTLB Repo Init

Initialize a fresh clone of `dlgrv/HowToLiveBetter` for translation work.

## Quick start

```bash
git clone https://github.com/dlgrv/HowToLiveBetter.git
cd HowToLiveBetter
git remote add upstream https://github.com/eternity4719/HowToLiveBetter.git
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Verification

```bash
make help
make status
make verify CH=01 LANG=ru
```

## Directory structure

```
run/                     # transient working state (gitignored)
tools/
  digest/                #   chapter splits (gitignored)
  .status/               #   verification results (gitignored)
  runs/                  #   wave pipeline state (gitignored)
  validate/              #   quality pipeline
  prompts/               #   LLM judge prompts
  rules/                 #   language rules
```

## Orchestration (committed)

| File | Purpose |
|---|---|
| `pipeline.yaml` | Tool topology: inputs/outputs, dependencies |
| `waves.json` | Wave plan: 1-3 chapters per wave |
| `translations.json` | Status manifest per language |
| `Makefile` | Entry points |
| `AGENTS.md` | Agent rules |

## Pitfalls

- Never commit `run/`, `tools/digest/`, `tools/.status/`, `tools/judge/`.
- Run upstream sync first: `make sync-upstream`.
- API keys in `.env` (gitignored). See `.env.example`.
- Python 3.10+ required.
