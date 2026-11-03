# Russian Marketplaces Product Recovery Guide

## Cross-Platform Search Strategy

When Ozon, Wildberries, or other major Russian marketplaces block direct access to a product page, use these techniques to find the same product elsewhere:

### 1. Extract Product Identifiers

From the blocked URL or description, extract:
- **Model number**: e.g., `A01`, `S`, `912936561`
- **Exact product name**: e.g., "tomtoc Accordion Accessory Pouch"
- **Variant details**: color, size, capacity
- **Brand name**: tomtoc, Apple, Samsung, etc.

**Example**: from Ozon URL `.../product/sumka-organayzer-tomtoc-...-912936561/` →
- Model: Accordion Accessory Pouch A01
- SKU: 912936561
- Search terms: "tomtoc accordion", "912936561"

### 2. Cross-Platform Search

Use web search with site: operators to find the same product:

```bash
# Yandex Market
site:market.yandex.ru "tomtoc accordion"

# Official brand stores
site:icases.ru "accordion"
site:imobilestore.ru "tomtoc"

# Competitors
site:biggeek.ru "tomtoc"
```

### 3. Model Verification

When searching, verify the match is exact:
- Check for model numbers (A01, S, etc.) in titles/descriptions
- Confirm it's the same product, not just the same brand
- Watch for color/size variants (Navy Blue ≠ Black)

### 4. Price Collection

Record:
- Platform name (Yandex Market, iCases, etc.)
- Exact price (₽)
- Availability status ("в наличии", "под заказ")
- Pickup locations if applicable
- Currency and any fees/shipping

### 5. Official Store Priority

Prefer official brand stores when available:
- iCases.ru for tomtoc products
- Brand's own website
- Higher reliability for authenticity and warranty

## Fallback Sources

### 6. Archive Recovery

If direct search fails, try:
- Wayback Machine snapshots of the original product page
- archive.today for recent copies
- Jina Reader if API key available

### 7. Browser Tools

As last resort, use browser tools to navigate:
- Try to find the product via search forms
- Look for category pages that may list the item
- Accept that some sites may be completely inaccessible

## Common Russian Marketplaces

| Platform | Focus | Best For |
|----------|-------|----------|
| **Yandex Market** | General | Price comparison, wide selection |
| **iCases.ru** | Official brand stores | Authenticity, warranty, pickup in Moscow |
| **i-mobilestore.ru** | Electronics | Tech accessories, gadgets |
| **Big Geek** | Electronics | Gaming, tech, niche gadgets |
| **Citilink** | Electronics | Computers, phones, accessories |
| **DNS** | Electronics | Wide range of tech products |
| **Svyaznoy** | Electronics | Phones, accessories, telecom |

## Pitfalls to Avoid

- **False positives**: Generic category pages masquerading as exact product matches
- **Variant confusion**: Mixing different colors/sizes in price comparisons
- **Availability errors**: "в наличии" may mean only in certain regions
- **Price volatility**: Russian e-commerce prices change rapidly
- **API blocks**: Some marketplaces block automated access entirely

## Real Example: tomtoc Accordion Accessory Pouch A01

- **Yandex Market**: 3 759 ₽ (navy blue, in stock)
- **iCases.ru**: 4 590 ₽ (black, in Moscow stores)
- **i-mobilestore.ru**: 3 858 ₽ (black, out of stock)
- **Big Geek**: No match found

**Cheapest**: Yandex Market at 3 759 ₽