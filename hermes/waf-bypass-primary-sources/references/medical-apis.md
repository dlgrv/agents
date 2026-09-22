# Medical Interaction APIs — Primary Sources

When drugs.com or similar checkers are WAF-blocked, use these APIs to extract
interaction data directly from authoritative sources.

## DailyMed (FDA) — XML API

**Search by drug name:**
```bash
curl -s "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}"
```

**Get full label XML:**
```bash
curl -s "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"
```

**Extract Drug Interactions section:**
- Search for `<title>DRUG INTERACTIONS</title>` in XML
- Extract content until next `<title>` or end of document
- Use XML parsing (not regex) for reliability

**Example workflow for tirzepatide:**
```bash
# Get setid for Mounjaro
setid=$(curl -s "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name=tirzepatide" | \
        jq -r '.data[0].setid')
# Fetch full XML
curl -s "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/${setid}.xml" -o mounjaro.xml
# Extract interactions section (Python example)
python3 << 'EOF'
import xml.etree.ElementTree as ET
import re

tree = ET.parse('mounjaro.xml')
root = tree.getroot()

# Find Drug Interactions section by title
for elem in root.iter():
    if elem.tag == 'title' and 'DRUG INTERACTIONS' in elem.text:
        # Get next siblings until next title
        section = []
        for sibling in elem.itersiblings():
            if sibling.tag == 'title':
                break
            section.append(sibling.text or '')
        print(''.join(section).strip())
        break
EOF
```

## EMA SmPC (European) — Web Scraping

**Search medicines.org.uk:**
```bash
curl -s "https://www.medicines.org.uk/emc/search?q={drug_name}"
```

**Extract interaction section:**
- Look for links containing "emc/product/" and "smpc"
- Navigate to section 4.5 "Interaction with other medicinal products"
- Use browser tools if site is JavaScript-heavy

## NIH RxNav — Drug Interaction API (if available)

**Resolve drug codes:**
```bash
curl -s "https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
```

**Check interactions (unstable API):**
```bash
curl -s "https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcues={code1}+{code2}"
```

**Note:** RxNav API frequently returns 404 or 503 — always have DailyMed fallback.

## Provenance Template

When citing from primary sources:

```markdown
> Drug interaction data extracted from official FDA label, accessed [YYYY-MM-DD],
> DailyMed (dailymed.nlm.nih.gov). Not live data — regulatory document.
```

## Common Drug Name Mappings

| Brand | Generic | DailyMed Search |
|-------|----------|----------------|
| Mounjaro | tirzepatide | "tirzepatide" or "mounjaro" |
| Seroquel | quetiapine | "quetiapine" or "seroquel" |
| Prozac | fluoxetine | "fluoxetine" or "prozac" |
| Trileptal | oxcarbazepine | "oxcarbazepine" or "trileptal" |
| Vitamin D3 | colecalciferol | "colecalciferol" or "cholecalciferol" |
| Folic acid | folic acid | "folic acid" |

## Pitfall: XML Structure Changes

DailyMed XML changes between label versions. Never rely on:
- Fixed line numbers
- Specific element positions
- Hardcoded section numbers (7.1, 7.2, etc.)

Always search by section title content and use XML traversal.
