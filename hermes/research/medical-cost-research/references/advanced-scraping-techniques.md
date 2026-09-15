# Advanced Scraping Techniques for Medical Pricing

This reference covers advanced techniques for extracting pricing data from modern medical lab websites that use JavaScript rendering, APIs, and other anti-scraping measures.

## User-Agent Masking for SPA Sites

Some modern web applications (React, Vue, Angular) return empty HTML shells to regular browsers but render complete content for search engine crawlers. Use Googlebot User-Agent to access full HTML:

```python
import urllib.request

BOT = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
def fetch_with_bot(url):
    req = urllib.request.Request(url, headers={'User-Agent': BOT})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
```

**When to use:** When regular `web_extract` returns empty or minimal HTML from React/Vue/Angular sites.

## JS Bundle Analysis for API Endpoints

Modern sites often embed API endpoints in JavaScript bundles. Extract these by:

1. **Download JS files from the page:** Look for `<script src="/local/js/*.js">` or similar
2. **Search for API patterns:** Use regex to find `/golk/tests/api/v1/`, `cityID`, `tests/`, etc.
3. **Find configuration objects:** Look for objects containing city IDs and API base URLs

**Example:** Invitro's config.js contains city IDs and API endpoints

```python
# Extract city ID and API base from JS
import re
js_content = open('invitro_config.js').read()
city_id = re.search(r'cityID\s*:\s*"([^"]+)"', js_content)
api_base = re.search(r'apiBaseUrl\s*:\s*"([^"]+)"', js_content)
```

## Batch API Requests

When provider APIs support pagination or batch requests, use them to efficiently gather large datasets:

```python
# Example: Invitro batch complex list
base_url = "https://www.invitro.ru/golk/tests/api/v1/complexes?cityID=f1c3c4f0-3426-4cda-8449-e5d326e02f97&limit=100&offset={}"

complexes = []
for offset in range(0, 1000, 100):
    url = base_url.format(offset)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    if not data.get('complexes'):
        break
    complexes.extend(data['complexes'])
```

**Key parameters:**
- `limit`: Max results per page (typically 50-200)
- `offset`: Starting position for pagination
- `cityID`: Required for regional pricing

## Catalog-First Approach

When individual test pages lack prices, scrape the full catalog and extract pricing from there:

1. **Fetch the main catalog page:** e.g., `/analizy-i-tseny/katalog-analizov/msk/`
2. **Extract all test URLs and names:** Use regex or HTML parsing
3. **For each test:** Either extract price from catalog or visit individual page
4. **Handle pagination:** Use `offset` parameters for large catalogs

**Example for CMD:**

```python
# CMD catalog approach
catalog_url = "https://www.cmd-online.ru/analizy-i-tseny/katalog-analizov/msk/"
h = fetch_with_bot(catalog_url)

# Extract all test URLs
test_urls = re.findall(r'/analizy-i-tceny/katalog-analizov/msk/[^/]+/', h)

# For each URL, extract price
for url in test_urls:
    if 'holesterin' in url or 'lipid' in url:
        test_h = fetch_with_bot(f"https://www.cmd-online.ru{url}")
        price = extract_price(test_h)  # Custom price extraction
```

## Handling Missing Complex Prices

Some providers don't publish complex test prices on individual test pages. Solutions:

1. **Search API:** Use provider search endpoints with complex codes
2. **Complex-specific endpoints:** Some APIs have `/complexes/by-article?article=CODE`
3. **Contact support:** For critical missing data

**Example:** CMD lipid complex (code 300341) may require direct inquiry

## Error Handling and Fallbacks

- **Timeout handling:** APIs may be slow; implement retry logic
- **Rate limiting:** Some APIs limit requests per minute
- **Data validation:** Always verify returned JSON structure
- **Fallback to scraping:** When APIs fail or return incomplete data

## Provider-Specific Notes

### Invitro
- Requires Googlebot User-Agent for full HTML
- API endpoints: `/golk/tests/api/v1/tests/`, `/complexes/by-article`
- City ID required: Moscow = `f1c3c4f0-3426-4cda-8449-e5d326e02f97`
- Complex prices often exclude blood draw fees

### Gemotest
- Static HTML pages, easy to scrape
- Complex tests like "Biokhimia 13" available in catalog
- Blood draw fee: 330 rubles

### CMD
- Catalog scraping required for comprehensive pricing
- Some complex prices not published on individual pages
- Blood draw fee: 285 rubles

### Helix
- Similar structure to Gemotest
- Often cheaper for same tests
- Static HTML pages

## Best Practices

1. **Always try official APIs first** when available
2. **Use Googlebot User-Agent** for JS-rendered sites
3. **Batch requests** for large datasets
4. **Verify prices** on at least two different pages when possible
5. **Document source** and date of price data
6. **Include all mandatory fees** (blood draw, processing) in totals
7. **Check for bundle discounts** before calculating individual test costs