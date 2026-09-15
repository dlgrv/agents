# Astro / client-island props extraction

Used when a target site's `<body>` is an empty shell and the real content is serialized
into a client-island attribute (e.g. `<astro-island props="{...}">`). The 6-step DOM
extraction returns almost nothing in this case, so you must decode the `props` payload.

## Detection (fetch raw HTML with `curl` first)

Look for ANY of:
- `<meta name="generator" content="Astro v6...">`
- `<astro-island ... props="{...}" component-url="/_astro/...">`
- `<body>` containing only `<h1 class="sr-only">...</h1> <astro-island></astro-island>`

Real example (probablynothing.xyz): the entire "desktop OS" UI — 13 artists, their
folder covers, social links, and a 44-name backer list — lived only in the `props`
JSON. The static DOM was a single `<h1>` + empty island.

## The wire format

Astro serializes props as `[tag, payload]`:
- `tag 0` -> literal primitive OR a plain object (already-decoded JSON)
- `tag 1` -> array of `[tag, payload]` (recurse)

The attribute is HTML-escaped: `&quot;` = `"`, `&amp;` = `&`.

## Worked script (validated on probablynothing.xyz)

```python
import re, json, html as H

raw = open('pn.html', encoding='utf-8').read()

# 1) grab the props payload (HTML-escaped, so use re.S and decode)
m = re.search(r'props="(\{.*?\})"', raw, re.S)
props = H.unescape(m.group(1)).replace('&quot;', '"').replace('&amp;', '&')
data = json.loads(props)

# 2) recursively unwrap Astro's [tag, value] envelope
def walk(v):
    if isinstance(v, list):
        if len(v) == 2 and isinstance(v[0], int):
            return [walk(x) for x in v[1]] if v[0] == 1 else walk(v[1])
        return [walk(x) for x in v]
    if isinstance(v, dict):
        return {k: walk(x) for k, x in v.items()}
    return v

clean = walk(data)
authors = clean['authors']          # list of plain dicts: name, id, image, info, folders, links, apps
for a in authors:
    print(a['name'], a['id'], 'folders=', len(a.get('folders') or []))

# 3) save for the clone build
json.dump(clean, open('pn_clean.json', 'w'), ensure_ascii=False, indent=1)
```

## Gotchas observed

- `a[1]` indexing fails if you forget the envelope is `[tag, value]` at EVERY level.
  The `walk()` above handles nested objects/arrays uniformly — use it, don't hand-index.
- CDN images (DigitalOcean Spaces `ams3.cdn.digitaloceanspaces.com`) returned `200` on
  plain `curl` with no auth/Referer. Reuse the real URLs directly in the clone <img src>.
- Backer names may NOT be in the `props` (they were in the SSR text of the real site but
  stripped from the island in some builds). When missing, recover them from the attached
  page text or a `curl` of the rendered HTML, then
  `re.findall(r'\b(\d{1,3})\s+([A-Za-z0-9_]+)\b', html)` filtered to `1 <= int(num) <= N`.

## Verification without a browser

After building the clone as a single `index.html`:
```bash
python3 -m http.server 8911 &          # background
curl -s -o /dev/null -w "page: %{http_code}\n" http://localhost:8911/index.html
curl -s http://localhost:8911/index.html | grep -o 'Not collective\|Vova Esenin\|golfmastermax'
# confirm each CDN asset is live
for u in img1 img2 ...; do curl -s -o /dev/null -w "%{http_code} $u\n" "$u"; done
```
All four must be `200` and the `grep` must print the known artist/backer names.
This proves the artifact is real without ever opening a browser.

## When to use vs. the 6-step DOM workflow

Use the 6-step DOM workflow (Step 1-6 of the parent skill) when the page has a real static DOM.
Use THIS technique when `<body>` is an empty shell / the site is an Astro/SSR island.
If unsure, `curl` the raw HTML and check for `<astro-island>` first — it's a 5-second tell.
