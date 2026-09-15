# Extraction & rendering recipes for website clones

## 1. Pull the real source + assets
```bash
curl -sL "https://TARGET/" -o page.html
# find linked stylesheets / json
grep -oE '/_astro/[A-Za-z0-9_.-]+\.css|/assets/[A-Za-z0-9_.-]+\.css' page.html
# verify a CDN image returns 200
curl -o /dev/null -w "%{http_code}\n" "https://cdn.example.com/foo.png"
```

## 2. Astro client-rendered island: unwrap props JSON
The page body is an empty shell with one big `<astro-island component-url=... props="{...}">`.
The `props` attribute is JSON **with HTML entities escaped** (`&quot;` `&amp;` `&lt;`). Decode first, then unwrap the Astro encoding:

- Each value is `[tag, val]` where `tag` is an int:
  - `0` = primitive (string/number/bool/null) → take `val`
  - `1` = array → `val` is a list of `[0, item]` entries → recurse
  - `2` = regex, `3` = Date, `4` = Map, `5` = Set ... (rare in UI data)
- A record/object is `[1, {key: [0, val], ...}]` → becomes `{key: val, ...}`.

Python recipe:
```python
import re, json, html as H
raw = open('page.html', encoding='utf-8').read()
m = re.search(r'props="(\{.*?\})"', raw, re.S)
props = H.unescape(m.group(1)).replace('&quot;','"').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
data = json.loads(props)

def walk(v):
    if isinstance(v, list):
        if len(v) == 2 and isinstance(v[0], int):
            if v[0] == 1:            # array
                return [walk(x) for x in v[1]]
            return walk(v[1])         # primitive / object
        return [walk(x) for x in v]
    if isinstance(v, dict):
        return {k: walk(x) for k, x in v.items()}
    return v

clean = walk(data)
# clean['authors'] is now a normal list of dicts with name/image/folders/links/...
```
Note: `data` top-level itself is `[1, {...}]`, so call `walk(data)` not `data['x']`.

## 3. Headless Chrome screenshot (when browser_exec is blocked)
`browser_exec` may be stuck on a "Allow remote debugging?" popup. Use a real Chrome binary instead:
```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# screenshot a URL
rm -f /tmp/out.png
"$CHROME" --headless=new --no-sandbox --disable-gpu \
  --user-data-dir=/tmp/shotprofile --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1440,900 --virtual-time-budget=7000 \
  --screenshot=/tmp/out.png "https://TARGET/" >/tmp/shot.log 2>&1
# Chrome HANGS on its background updater even after out.png is written.
# Run it via terminal(background=true), then in a SEPARATE call: ls -la /tmp/out.png
# confirm it exists, then process(action='kill').
```
- For local files use `http://localhost:PORT/index.html` (serve with `python3 -m http.server PORT`).
- `--dump-dom` prints the post-JS DOM to stdout (use to confirm JS-generated elements rendered): grep the output for generated class names like `class="icon"` or `class="window emoji"`.
- If the screenshot is wrong/empty, the JS probably errored — grep the `--dump-dom` output; a missing generated element means an early throw (check JSON parse / placeholder not replaced).

## 4. CDP / chrome-devtools-mcp on :9222 IPv4-vs-IPv6 trap
Two Chrome processes can share `:9222`:
- personal Chrome → binds IPv4 `127.0.0.1` → `/json` returns **404**
- debuggable Chrome → binds IPv6 `[::1]` → `/json/version` works

A MCP server pointed at `http://127.0.0.1:9222` connects to the personal Chrome and fails.
Use `http://localhost:9222` or `http://[::1]:9222`. `curl http://[::1]:9222/json/version` works;
the `websocket-client` WS upgrade to `ws://[::1]:9222/devtools/browser/...` may still drop the
handshake — prefer the `--screenshot`/`--dump-dom` binary route above.
