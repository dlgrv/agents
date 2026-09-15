# Provider API Endpoints

This reference documents internal API endpoints for medical labs that expose pricing data programmatically.

## Invitro (Russia)

Invitro uses a React-based frontend with internal API endpoints. Most endpoints require a city ID (e.g., Moscow: `f1c3c4f0-3426-4cda-8449-e5d326e02f97`).

### Base API URL
```
https://www.invitro.ru/golk/tests/api/v1/
```

### Endpoints

#### Get Test by ID
```bash
https://www.invitro.ru/golk/tests/api/v1/tests/{test_id}?cityID={city_id}
```
- Returns individual test price and details
- Example: `https://www.invitro.ru/golk/tests/api/v1/tests/9?cityID=f1c3c4f0-3426-4cda-8449-e5d326e02f97` (ОАК)

#### Get Test by Article/Code
```bash
https://www.invitro.ru/golk/tests/api/v1/tests/by-article?article={article}&cityID={city_id}
```
- Useful when you know the test code (e.g., "ОБС54")
- Returns price and details
- Example: `https://www.invitro.ru/golk/tests/api/v1/tests/by-article?article=ОБС54&cityID=f1c3c4f0-3426-4cda-8449-e5d326e02f97`

#### Get Complex by Article/Code
```bash
https://www.invitro.ru/golk/tests/api/v1/complexes/by-article?article={article}&cityID={city_id}
```
- Returns complex test price and included tests
- Example: `https://www.invitro.ru/golk/tests/api/v1/complexes/by-article?article=ОБС54&cityID=f1c3c4f0-3426-4cda-8449-e5d326e02f97` (Липидный профиль: скрининг)

#### Get Complex List
```bash
https://www.invitro.ru/golk/tests/api/v1/complexes?cityID={city_id}&limit=100&offset={offset}
```
- Paginated list of all available complexes
- Use `offset` to paginate through results

### Notes
- API returns JSON with `price`, `title`, `code` fields
- Complexes include `tests` array with individual test details
- Some APIs return prices without mandatory fees (blood draw not included)
- Requires proper User-Agent (try Googlebot if regular requests fail)
- City IDs are required and vary by region

## Other Providers

### Gemotest
- Catalog pages are static HTML, accessible via `web_extract`
- No known public API endpoints
- Complex test codes like "ОБС54" may work in search URLs

### Helix
- Similar structure to Gemotest
- Some pricing available via search pages
- No known public API endpoints

### General Tips for API Discovery

1. **Browser DevTools:** Check Network tab for API calls when browsing test pages
2. **JS Bundle Analysis:** Search for API patterns in minified JS files (e.g., `/golk/tests/api/v1/`)
3. **User-Agent Testing:** Some APIs respond differently to Googlebot vs regular browsers
4. **City IDs:** Usually found in JS config files or API responses
5. **Authentication:** Most APIs don't require authentication for public pricing data

## Example Usage

```python
import urllib.request, urllib.parse, json

# Get individual test
url = "https://www.invitro.ru/golk/tests/api/v1/tests/9?cityID=f1c3c4f0-3426-4cda-8449-e5d326e02f97"
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))
print(f"{data['title']}: {data['price']} руб.")

# Get complex test
url = "https://www.invitro.ru/golk/tests/api/v1/complexes/by-article?article=ОБС54&cityID=f1c3c4f0-3426-4cda-8449-e5d326e02f97"
response = urllib.request.urlopen(url)
data = json.loads(response.read().decode('utf-8'))
print(f"{data['title']}: {data['price']} руб.")
for test in data['tests']:
    print(f"  - {test['title']}")
```