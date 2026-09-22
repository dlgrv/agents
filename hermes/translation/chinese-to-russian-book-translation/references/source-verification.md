# Source verification for translated books

## Overview

When working with translated content, especially in domains like health, safety, and finance, verify all claims against authoritative sources. This protocol ensures accuracy and reliability of translated information.

## Verification workflow

### Step 1: Identify TODO flags
- Look for «待核实»/TODO markers in source text
- Prioritize by impact (safety-critical first)
- Use exact-match search for the claim in official sources

### Step 2: Source lookup and citation extraction
- Use primary sources (CDC, WHO, S&P, official PDFs)
- Capture direct quotes from source pages
- Include full citation with DOI/URL and access date
- Preserve original phrasing and punctuation

### Step 3: Cross-verification
- Use Wayback snapshots if WAF blocks live sites
- Cross-check DOI metadata with Crossref API
- Verify PDF text extraction matches claimed content
- Ensure multiple sources agree on key facts

### Step 4: Source replacement
- Replace TODO with full citation including exact quote
- Update evidence等级 (C→B for verified sources)
- Remove «待核实» marker
- For author experience claims (作者经验), keep with disclaimer

## Source types by priority

| Priority | Source type | Examples | Handling | Verification method |
|---------|-------------|----------|----------|-------------------|
| **Critical** | Health/safety agencies | CDC, WHO, NPS, CPSC | Replace TODO with exact citation | Wayback if WAF blocked |
| **High** | Financial/statistical | S&P, CNNIC, official PDFs | Replace TODO with official data | Crossref/PDF text extraction |
| **Medium** | Industry standards | NFPA, ERC, AAP | Replace with official guidance | Archive.org lookup |
| **Low** | Author experience | Marked as 作者经验 | Keep as is, add disclaimer | None needed |

## Common patterns to verify

- **Emergency numbers**: 120 → 103/112, 119 → 101, 110 → 102
- **Financial statistics**: SPIVA fund underperformance rates, CNNIC internet usage data
- **Medical guidance**: CPR steps, choking protocols, CO detector placement
- **Government agencies**: 民政 → органы соцзащиты, 卫健委 → Минздрав
- **Legal terms**: 低保 → дибао (with gloss), 兵役法 → закон о воинской обязанности

## Quality gates

- **All citations must have URLs/DOIs** — No bare «来源：作者经验» without disclaimer
- **Exact quote matching** — Source text must match the cited passage exactly
- **Live URL verification** — Check that cited URLs resolve (use Wayback if blocked)
- **PDF verification** — Official PDFs must be extractable and match claimed content
- **Cross-source consistency** — Multiple sources should agree on key facts
- **Independent review required** — Critical claims require verification by second reviewer

## Pitfalls

- **WAF blocking** — Many official sites block automated access; use Wayback snapshots
- **PDF extraction failures** — Some PDFs are images-only; use OCR or official text versions
- **Outdated statistics** — Always check publication dates; use most recent available data
- **Translation artifacts** — Verify that translated terms match source concepts exactly
- **Missing context** — Some facts require country-specific context; add translator notes when needed
- **False positives in search** — Use exact-match search with quoted phrases, not keyword matching
- **Citation glue errors** — Never combine multiple source sentences into one citation
- **Source title mismatch** — Verify that cited titles match actual source documents
- **Date verification** — Always check that cited sources are current (e.g., ERC 2021 does not contain claimed sections)
- **Wayback date drift** — Use earliest possible Wayback snapshot to avoid page changes

## Verification commands

```bash
# Wayback snapshot for WAF-blocked sites
python3 -c "import urllib.request, re; t = urllib.request.urlopen(...).read().decode('utf-8'); print(re.search(r'65%', t).group())"

# Crossref DOI lookup
curl -s "https://api.crossref.org/works/10.1111/j.1540-6261.2010.01598.x" | jq '.message.title[0]'

# PDF text extraction
pdftotext -layout /path-to/report.pdf - | grep -A 5 "人均每周"

# Independent review protocol
gh issue create --title "Fact-check verification" --body "Provide exact quote from source: [citation]"
```