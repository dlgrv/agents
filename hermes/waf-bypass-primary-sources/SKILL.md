---
name: waf-bypass-primary-sources
description: "Bypass WAF blocks via authoritative FDA/EMA sources."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, WAF, Bypass, Medical, Regulatory]
    related_skills: [blocked-page-recovery, grounded-citations]
---

# WAF Bypass via Primary Sources

When an entire domain is WAF-blocked (Access Denied on all pages), and archives
fail, don't waste time on proxies or retries. Instead, use the **authoritative
primary sources** that third-party services scrape from.

## When to use this

- Medical checkers (drugs.com, RxList) are globally blocked
- Government sites with aggressive bot protection
- Paywalled databases where archives are incomplete
- Any domain returning 403/404/503 on *every* endpoint

## Primary sources by domain

| Domain Type | Primary Source | Use Case |
|-------------|----------------|-----------|
| **US drugs/interactions** | DailyMed (dailymed.nlm.nih.gov) | Official FDA labels, Drug Interactions sections |
| **EU drugs/interactions** | EMA SmPC (medicines.org.uk) | European product characteristics |
| **Clinical trials** | ClinicalTrials.gov (if accessible) | Trial protocols, results |
| **Drug databases** | NIH RxNav (rxnav.nlm.nih.gov) | Drug interaction API (if available) |
| **Medical literature** | PubMed (if accessible) | Peer-reviewed studies |
| **Regulatory docs** | FDA/EMA.gov, govinfo.gov | Approvals, labels, safety updates |

## Workflow for blocked medical domains

### 1. Map the blocked domain to its primary source

If drugs.com is blocked:
- Search DailyMed for each drug's official label
- Use the XML API for reliable section extraction
- Cross-check with EMA SmPC for European data

### 2. Extract structured data from primary sources

**FDA DailyMed (XML API):**
```bash
# Search for drug by name
curl -s "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=tirzepatide"
# Get full label XML
curl -s "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"
```

**EMA SmPC (web scraping):*
- Search medicines.org.uk for the drug
- Navigate to the "Summary of Product Characteristics"
- Extract sections 4.5 (Interactions) and 4.8 (Undesirable effects)

**NIH RxNav (if available):**
- Resolve RxNorm codes for each drug
- Query interaction API for pairwise checks

### 3. Preserve provenance and citations

Every primary source copy MUST be cited with its provenance:

| Source | Provenance | Citation format |
|--------|------------|----------------|
| DailyMed | `official` | "FDA label, accessed [date], DailyMed" |
| EMA SmPC | `official` | "EMA SmPC, accessed [date], medicines.org.uk" |
| RxNav | `official` | "NIH RxNav, accessed [date], rxnav.nlm.nih.gov" |

## Pitfalls to avoid

- **Never present a primary source as live data** — cite it as an official document
- **DailyMed XML structure changes** — search by section title, not line numbers
- **RxNav API is unstable** — have a fallback to manual label extraction
- **Cross-reference when possible** — FDA and EMA labels sometimes differ
- **Validate extraction completeness** — ensure you got the full interaction section

## Integration with blocked-page-recovery

Use this skill when `blocked-page-recovery` fails on domain-wide blocks:
1. Try `blocked-page-recovery` first (archives, Jina, etc.)
2. If all routes fail (domain-wide WAF), switch to primary sources
3. Extract the needed data directly from authoritative documents

This approach is more reliable than fighting WAFs and gives you the original,
uncorrupted data that third-party checkers summarize and sometimes misinterpret.
