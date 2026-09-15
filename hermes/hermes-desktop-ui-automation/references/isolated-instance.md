# Isolated Hermes desktop instance (mock-backed, CDP-open)

Full recipe for a **throwaway** desktop instance that runs against its own
`HERMES_HOME` (never `~/.hermes`), talks to a **mock** LLM so no API keys or
real chats are touched, and opens the CDP port so you can drive/inspect it.
Companion to the `hermes-desktop-ui-automation` skill.

## Why this exact shape

- `HERMES_HOME` = data dir (config.yaml, API keys, `state.db` chat history).
  Omit it → falls back to `~/.hermes` and **writes test messages into the
  user's real session history** (incident 2026-08-26).
- A throwaway `HERMES_HOME` with **no backend** boots, but the composer renders
  `contentEditable=false` (disabled) because the backend never became ready. To
  get an *enabled, typeable* composer you must give it a working backend — the
  cheapest path is a mock HTTP server + a venv with `yaml` installed.
- `HERMES_DESKTOP_DEV_SERVER` is required for the CDP port to open
  (`electron/dev-cdp.ts` closes it with no dev server). Point it at a running
  vite.
- `--user-data-dir` only dodges Electron's single-instance lock; it is NOT a
  substitute for `HERMES_HOME`.

## Setup (one-time per machine)

```bash
cd ~/github/hermes-agent
# Python venv with desktop backend deps (system python lacks `yaml`, backend exits)
uv venv .venv && uv pip install -e . --quiet
# Build the renderer dist (dev:electron needs it)
cd apps/desktop && npm run build
```

## Launch sequence (verified working)

Terminal 1 — mock inference server (OpenAI-compatible, canned reply):
```bash
cd ~/github/hermes-agent/apps/desktop
node -e '
const http=require("http");
const s=http.createServer((req,res)=>{
  res.setHeader("Access-Control-Allow-Origin","*");
  if(req.method==="POST"&&req.url.startsWith("/v1/chat/completions")){
    let b="";req.on("data",c=>b+=c);req.on("end",()=>{
      res.writeHead(200,{"Content-Type":"text/event-stream"});
      const words="Hello from isolated debug sandbox.".split(" ");
      let i=0;const tick=()=>{if(i>=words.length){res.write("data: [DONE]\n\n");res.end();return;}
        const w=i===0?words[i]:" "+words[i];
        res.write("data: "+JSON.stringify({id:"m",object:"chat.completion.chunk",choices:[{index:0,delta:{content:w}}]})+"\n\n");i++;setTimeout(tick,30);};
      tick();
    });return;
  }
  res.writeHead(404);res.end("nf");
});
s.listen(53999,"127.0.0.1",()=>console.log("mock inference on 53999"));
'
```

Terminal 2 — vite renderer (background; needed for `HERMES_DESKTOP_DEV_SERVER`):
```bash
cd ~/github/hermes-agent/apps/desktop
npm run dev:renderer      # serves http://127.0.0.1:5174
```

Terminal 3 — isolated electron + CDP + mock backend:
```bash
cd ~/github/hermes-agent/apps/desktop
# 1. isolated home + mock provider config
mkdir -p /tmp/hermes-debug-home
cat > /tmp/hermes-debug-home/config.yaml <<'YAML'
model: { default: mock-model, provider: mock }
providers:
  mock: { api: http://127.0.0.1:53999/v1, name: Mock, api_mode: chat_completions,
          key_env: MOCK_API_KEY, models: { mock-model: {} }, context_length: 4096 }
YAML
echo "MOCK_API_KEY=debug" > /tmp/hermes-debug-home/.env
# 2. launch (visible window opens — warn the user first)
HERMES_HOME=/tmp/hermes-debug-home \
HERMES_DESKTOP_PYTHON=~/github/hermes-agent/.venv/bin/python \
HERMES_DESKTOP_CDP_PORT=9333 \
HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
HERMES_DESKTOP_USER_DATA_DIR=/tmp/cdp-sandbox-userdata \
HERMES_DESKTOP_IGNORE_EXISTING=1 \
  ~/github/hermes-agent/apps/desktop/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron . \
  --user-data-dir=/tmp/cdp-sandbox-userdata
```

Verify CDP:
```bash
nc -z -w 3 127.0.0.1 9333 && echo OPEN || echo closed
curl -s --max-time 3 http://127.0.0.1:9333/json/list | python3 -c "import json,sys; d=json.load(sys.stdin); print([t['url'][:60] for t in d if t['type']=='page'])"
```

## Driving it (real input events matter)

- Use real CDP `Input.dispatchKeyEvent` / `dispatchMouseEvent`, not synthetic
  `dispatchEvent` — React handlers and blur→cancel races only reproduce with
  real events.
- **Sending a message:** click composer → `ui_type` → `ui_press(Enter)` does NOT
  submit unless the composer keeps focus. The press step must re-focus the composer
  (`document.querySelector('[data-slot="composer-rich-input"]').focus()`) *before*
  dispatching keyDown/keyUp with `commands:['Enter']`. Without that, Enter is
  swallowed and `turnPair` stays empty.
- `npm run dev:mock` exists but (a) doesn't open CDP (no `HERMES_DESKTOP_DEV_SERVER`)
  and (b) its `findElectron()` only checks the Linux `dist/electron` path — it
  fails on macOS (`Electron.app/Contents/MacOS/Electron`). Prefer the manual
  sequence above until those are patched upstream.

## Cleanup
Kill the electron process (by PID), the vite process, and the mock node server.
`lsof -tiTCP:5174 -sTCP:LISTEN | xargs kill` etc. Remove `/tmp/hermes-debug-home`
if you don't need the session.
