---
name: medical-cost-research
description: "Research lab tests and procedures pricing across providers."
version: 0.1.0
author: Hermes Agent
license: MIT
nplatforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Medical, Health, Pricing, Research]
    related_skills: [product-price-monitor, blocked-page-recovery, grounded-citations]
---

# Medical Cost Research

Research and compare the cost of medical services, lab tests, and procedures across multiple providers in a region. This skill handles lab test naming variants, bundling discounts, hidden fees (venous blood draw), and aggregator sites that offer cached pricing. For ongoing monitoring, use `product-price-monitor`.

See also `references/lab-test-naming-variants.md`, `references/api-endpoints.md`, `references/advanced-scraping-techniques.md`, `references/maximizing-savings.md`, and `references/code-verification.md` for advanced techniques, optimization strategies, and code verification best practices.

## When to Use

- "How much does a complete blood test cost in Moscow?"
- "Compare prices for a lipid panel across Invitro, Helix, Gemotest."
- "Find the cheapest provider for a thyroid panel."
- "How much is a venous blood draw fee?"
- "What's the cost of a full health checkup?"

Don't use for: medical advice, billing disputes, or one-off "what does this cost now" lookups (use `web_search`/`web_extract` directly).

## Procedure

### 1. Define the service and region

Record the exact test/procedure name(s), region/city, provider preferences, and any variants (venous vs capillary blood, fasting requirements, etc.). Done when the search cannot return ambiguous results.

### 2. Research provider pricing

Use multiple routes to gather pricing data:

- **Direct provider sites:** Use `web_extract` on lab test catalog pages, focusing on static HTML (SPA pricing is often JS-only and inaccessible). For JS-rendered sites (e.g., Invitro), try Googlebot User-Agent or check for internal API endpoints (e.g., `/golk/tests/api/v1/...`).
- **Aggregator sites:** HelloDoc, DocDoc, PriceDoc, and similar aggregators often cache provider prices and may show historical averages.
- **Price comparison sites:** Check for dedicated medical cost comparison tools.
- **Provider-specific search:** Use `web_search` with exact-match test names to find current pricing pages.
- **Mobile apps:** Provider apps (e.g., HelloDoc app) often have real-time pricing but may require login; check if they aggregate partner lab prices.
- **Provider APIs:** Some labs expose internal pricing APIs (e.g., Invitro's `/golk/tests/api/v1/tests/{id}?cityID=...`). Check for config files or JS bundles in the browser for API endpoints.

### 3. Handle naming variants

Lab tests have many names — map them:
- Complete blood count: ОАК, clinical blood test, general blood analysis
- Lipid panel: lipidogram, lipid profile, lipid complex, cholesterol panel
- Glycated hemoglobin: HbA1c, glycosylated hemoglobin
- TSH: TTG, thyroid-stimulating hormone
- Gamma-GT: Гамма-ГТ, ГГТ, GGT (note: often listed under 'ferments' or 'enzymes' section)

### 4. Account for bundling and extras

Many tests are cheaper in bundles:
- "Biokhimia 13" (Gemotest) covers most common blood tests for 1690 rubles vs 3500+ separately
- Always check if a "complex" or "panel" covers the individual tests needed
- Account for extra fees: venous blood draw (330 rubles), capillary blood (often included), processing fees
- **Physical clinics vs aggregator apps:** Physical clinics (e.g., HelloDoc.clinic) may have different pricing than aggregator apps that partner with labs (e.g., HelloDoc app partners with Gemotest/Helix). Check if the clinic offers blood draws on-site or if you must go to a separate lab.
- **API-based pricing:** When using provider APIs (e.g., Invitro's `/golk/tests/api/v1/complexes/by-article?article=...`), verify if the complex price includes individual test prices or if there are additional fees (some APIs return only the test price without the blood draw fee).

### 5. Compare and normalize

- Convert all prices to a common currency (usually local)
- Include all mandatory fees (blood draw, processing)
- Note if prices include VAT or are pre-tax
- Mark if prices are current or historical averages
- Check for discounts or promotions
- **Physical vs aggregator pricing:** If researching physical clinics (e.g., HelloDoc.clinic), verify if they offer lab services on-site or partner with external labs. Aggregator apps (HelloDoc app) often show partner lab prices but may have different clinic pricing.
- **API pricing normalization:** When comparing API-based prices (e.g., Invitro), verify if the API returns test prices with or without mandatory fees (some APIs return only the test price, requiring separate addition of blood draw fees).
- **Code vs name verification:** Always verify that test codes match the actual test content — some codes (e.g., GGT 090016 vs 090013) may refer to similar but distinct tests. When ordering, use the exact code from the provider's catalog to avoid receiving the wrong test.

### 6. Present results

Present pricing in a clear table format with:
- Provider name
- Test name (as listed by provider)
- Base price
- Any mandatory fees
- Total cost
- Currency
- Source/date of data
- Notes on bundling or special conditions
- **Physical clinic vs aggregator note:** If applicable, note whether the provider is a physical clinic offering services on-site or an aggregator partnering with external labs (e.g., "HelloDoc.clinic offers УЗИ on-site but blood tests via Gemotest partners").
- **API source note:** If using provider APIs (e.g., Invitro's internal API), note the endpoint used and whether prices include mandatory fees (e.g., "Prices from Invitro API /golk/tests/api/v1/...; blood draw fee not included").

## Provider-specific notes

### Gemotest (Russia)
- Catalog pages are static HTML, extractable with `web_extract`
- Complex tests like "Biokhimia 13" cover multiple individual tests
- Venous blood draw: 330 rubles
- Test names in Russian: use exact-match search
- **Maximizing savings:** When assembling a basket of tests, always check if "Biokhimia 13" (1690 rubles) covers most of your required blood chemistry tests — it often replaces 8-10 individual tests at significant savings

### Helix (Russia)
- Often cheaper than Gemotest for the same tests
- Uses similar catalog structure
- Good for price comparison
- **Maximizing savings:** Helix frequently offers the best pricing for thyroid panels and vitamin D tests — verify if their "vitamin D" test uses the same method (ELISA) as more expensive options before choosing

### Invitro (Russia)
- Prices often 20-40% higher than Gemotest/Helix
- Mostly JS-rendered, hard to scrape directly
- Check aggregators for cached pricing
- **API access:** Use their internal API endpoints (e.g., `/golk/tests/api/v1/tests/{id}?cityID=...`) for accurate pricing. City ID required (e.g., Moscow: `f1c3c4f0-3426-4cda-8449-e5d326e02f97`). Complex endpoints: `/complexes/by-article?article=...`.
- **Maximizing savings:** Invitro's "Липидный профиль: скрининг" (ОБС54) complex may be cheaper than individual tests, but verify it covers all required markers — sometimes individual tests are better priced

### CMD (Russia)
- Academic/research-focused lab, higher reputation for accuracy
- Some complex test prices not published online — may require phone inquiry
- Venous blood draw: 285 rubles
- **Maximizing savings:** CMD rarely offers bundle discounts — assembling tests individually is usually cheaper. Always call 8 (495) 120-13-12 to inquire about unpublished complex prices (e.g., "Biokhimia 8" code 300338) — if available, these may replace multiple individual tests
- **Vitamin D pricing:** CMD offers standard ELISA (080006) at 2175 rubles and advanced LC-MS/MS method at 3315 rubles — for routine screening, the standard method is sufficient and saves 1140 rubles

### HelloDoc/DocDoc aggregators
- Show prices from multiple providers
- May show historical averages or discounts
- Good for quick comparison across providers
- **Physical clinics vs aggregator apps:** HelloDoc.clinic is a physical clinic in Nekrasovka (Pokrovskaya St. 14) offering УЗИ on-site, while HelloDoc app is an aggregator that partners with labs like Gemotest/Helix for blood tests. Prices and services differ significantly between the clinic and the app.
- **Maximizing savings:** Aggregators show partner lab prices but may not reflect current promotions — always verify pricing on the actual lab's website before final decision

## Pitfalls

- Assuming test names are consistent across providers
- Forgetting mandatory fees like blood draws
- Not checking for bundle discounts
- Using JS-rendered pricing pages that can't be scraped
- Assuming aggregator prices are current
- Not accounting for regional price variations
- Confusing capillary and venous blood pricing
- **Physical vs aggregator confusion:** Mistaking HelloDoc.clinic (physical clinic offering УЗИ on-site) for HelloDoc app (aggregator partnering with labs). They have different pricing models and service offerings. Always verify if you're researching a physical clinic location or an aggregator app.
- **JS-rendered site pitfalls:** Some labs (Invitro) render prices via JavaScript. Try Googlebot User-Agent or look for internal API endpoints in browser JS bundles (search for `/golk/tests/api/v1/` or similar patterns).
- **API endpoint confusion:** Provider APIs may return prices without mandatory fees (e.g., blood draw). Always check if API prices need manual addition of extra fees.
- **API endpoint confusion:** Provider APIs may return prices without mandatory fees (e.g., blood draw). Always check if API prices need manual addition of extra fees.
- **Unpublished complex pricing:** Some labs (CMD) don't publish complex test prices online — always call to inquire about unpublished complexes that could replace multiple individual tests
- **Method overpricing:** Advanced methods (LC-MS/MS for vitamin D) cost 2-3x more than standard ELISA but provide same clinical utility for routine screening — choose standard methods unless specifically required
- **Complex vs individual calculation:** Always verify that complex tests cover ALL required individual tests — sometimes complexes miss one or two markers, making individual tests cheaper overall
- **Code vs content mismatch:** Test codes may not always correspond to the expected test content — verify that code 090016 (Gamma-GT) matches the actual test description, not just a similar code (e.g., 090013). When ordering, use the exact code from the provider's catalog to avoid receiving the wrong test.

## Verification

- [ ] At least three provider sources are compared
- [ ] All mandatory fees are included in totals
- [ ] Bundle savings are calculated correctly
- [ ] Prices are clearly marked as current or historical
- [ ] Test name variants are mapped correctly
- [ ] Results are presented in a clear, comparable format
- [ ] For JS-rendered sites, attempt API endpoints or Googlebot User-Agent before declaring inaccessible
- [ ] API-based pricing is verified to include/exclude mandatory fees
- [ ] Test codes are verified against actual test content before reporting
