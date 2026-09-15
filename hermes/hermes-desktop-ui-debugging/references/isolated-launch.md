# Isolated debug-launch recipe (proven end-to-end)

Goal: drive the Hermes desktop UI over CDP **without touching the user's real
`~/.hermes`**. This recipe was validated in the 2026-08-26 session: a message
was sent, the mock backend answered, and `ui_flow_edit` reproduced the edit
path — all in a throwaway `/tmp` home. Critically, it sets BOTH
`HERMES_HOME` (instance side) and `DESKTOP_DEBUG_MCP_EXPECTED_HOME` (server
side) so the fail-closed guard permits mutations.

## 1. Isolated home + mock provider config

```bash
mkdir -p /tmp/hermes-debug-home
cat > /tmp/hermes-debug-home/config.yaml <<'YAML'
model: { default: mock-model, provider: mock }
providers:
  mock:
    api: http://127.0.0.1:53999/v1
    name: Mock
    api_mode: chat_completions
    key_env: MOCK_API_KEY
    models: { mock-model: {} }
    context_length: 4096
YAML
echo "MOCK_API_KEY=debug" > /tmp/hermes-debug-home/.env
```

## 2. Mock inference server (any port, here 53999)

A tiny SSE chat-completions stub. Streams token-by-token so the renderer
renders a normal assistant turn.

```js
// mock-infer.mjs
const http = require('http')
const s = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*')
  if (req.method === 'POST' && req.url.startsWith('/v1/chat/completions')) {
    let b = ''; req.on('data', c => b += c); req.on('end', () => {
      res.writeHead(200, { 'Content-Type': 'text/event-stream' })
      const words = 'Hello from isolated debug sandbox.'.split(' ')
      let i = 0
      const tick = () => {
        if (i >= words.length) { res.write('data: [DONE]\n\n'); res.end(); return }
        const w = i === 0 ? words[i] : ' ' + words[i]
        res.write('data: ' + JSON.stringify({ id: 'm', object: 'chat.completion.chunk', choices: [{ index: 0, delta: { content: w } }] }) + '\n\n')
        i++; setTimeout(tick, 40)
      }
      tick()
    })
    return
  }
  res.writeHead(404); res.end('nf')
})
s.listen(53999, '127.0.0.1', () => console.log('mock inference on 53999'))
```

## 3. Renderer (vite, no window) + electron (visible window — WARN USER)

```bash
# terminal 1
cd ~/github/hermes-agent/apps/desktop && npm run dev:renderer   # vite :5174

# terminal 2 — opens a VISIBLE window, announce first
cd ~/github/hermes-agent/apps/desktop
HERMES_HOME=/tmp/hermes-debug-home \
HERMES_DESKTOP_PYTHON=$HOME/github/hermes-agent/.venv/bin/python \
HERMES_DESKTOP_CDP_PORT=9333 \
XCURSOR_SIZE=24 \
HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
HERMES_DESKTOP_USER_DATA_DIR=/tmp/cdp-sb \
HERMES_DESKTOP_IGNORE_EXISTING=1 \
node_modules/electron/dist/Electron.app/Contents/MacOS/Electron . \
  --user-data-dir=/tmp/cdp-sb

# poll
sleep 25; curl -s --max-time 3 http://127.0.0.1:9333/json/version
```

## 4. Debug MCP server (mutations allowed, guard satisfied)

```bash
cd ~/github/hermes-agent/apps/desktop/mcp
DESKTOP_DEBUG_MCP_ALLOW_ACT=1 \
DESKTOP_DEBUG_MCP_EXPECTED_HOME=/tmp/hermes-debug-home \
DESKTOP_DEBUG_MCP_PORT=9333 \
  node server.mjs
```

## 5. Driving it (the part that silently fails without the fix)

- `ui_click composer` then `ui_type` then `ui_press Enter` — but Enter only
  submits if the composer keeps focus. `ui_press` re-focuses the composer
  before dispatching and passes `commands: ['Enter']` (CDP detail that makes a
  real Enter land). Without that, the key is swallowed and the message never
  appears in the thread.
- If a turn pair still doesn't show after Enter in an isolated instance, click
  the real Send control by coordinates rather than relying on the keystroke.

## Cleanup

Kill the electron + vite + mock-server processes when done. The `/tmp` home
and its `state.db` are disposable.
