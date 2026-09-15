---
name: codebase-walkthrough
description: "Use when asked what a repo does or how its logic works."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [codebase, architecture, repo, walkthrough, comprehension, reverse-engineering]
---

# Codebase walkthrough — "what does this repo do?"

## When to use

User asks what a repo does, how the logic inside is organized, or wants an orientation map before touching it ("что тут делает репо?", "how does X work internally?"). Not for metrics/LOC (→ `codebase-inspection`), debugging (→ `systematic-debugging`), or planning changes (→ `plan`).

## Workflow

1. **README + docs first** (fast, no clone): fetch `raw.githubusercontent.com/<org>/<repo>/HEAD/README.md` and key docs (`docs/quickstart.md`, `benchmarks/README.md`) via curl. This gives the project's self-description and vocabulary.
2. **Shallow clone for anything deeper** — `git clone --depth 1 <url> /tmp/<name>`. More robust than parsing the GitHub API `git/trees` JSON (see pitfalls) and gives you grep-able files.
3. **Map the tree in one pass**: `find <pkg> -name '*.py' | sed 's|<root>/||' | sort` (or `ls` per top dir). Group by top-level package — the dir layout IS the architecture in well-organized repos.
4. **Read docstrings, not implementations.** `head -40` of the core modules: module docstrings in mature repos carry the design rationale (why, not just what). Pick 4–6 files from the directories the README emphasizes.
5. **Targeted grep to bind README claims to code**: README buzzwords (a policy name, a flag, a paper term) → `grep -rn '<term>' <pkg>/` to find where it actually lives. Never report a README claim you didn't locate in code.
6. **Synthesize**: (a) one-line "what it is + its core bet", (b) architecture map by directory with one line each, (c) 3–5 notable engineering details with file references, (d) ecosystem position (what it replaces / compares to).

## Pitfalls

- **GitHub API tree JSON can be poisoned**: a repo once had a tree entry with an embedded control character in its path — broke `json.loads` (needs `strict=False`) and a naive print of the parsed entry flooded stdout with 145k chars. Never print raw API payloads; extract fields in Python, print short summaries. If parsing gets weird, switch to shallow clone immediately.
- **Never paste file contents into the answer** — reference `path:line` (delegation rule). The answer is a map, not a mirror.
- **Keep clones in /tmp** and clean up (`rm -rf`) when done with the session's exploration.
- **Docstrings over source-reading marathons**: if after ~6 file heads the picture is clear, stop reading — depth beyond that is for follow-up questions only.
- Examples of prior walkthroughs live in `references/` — reuse as a format model, and check there first in case the repo was already walked (avoid re-cloning).

## Output shape

Structured answer in the user's chat language. Lead with the essence (what problem it solves, what's the core mechanism), then the directory map, then interesting details. No filler, no restating the question.

## Related

- `codebase-inspection` — quantitative LOC/language metrics (bundled skill, do not edit; this skill covers the qualitative side).