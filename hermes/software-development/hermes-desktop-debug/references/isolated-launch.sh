#!/usr/bin/env bash
# Isolated Hermes desktop debug launcher (macOS). Copy, set REPO, run.
# Starts: mock inference server (53999) + vite (5174) + electron (CDP 9333)
# against an isolated /tmp/hermes-debug-home. No real data is touched.
set -euo pipefail

REPO="${REPO:-$HOME/github/hermes-agent}"
DESKTOP="$REPO/apps/desktop"
HOME_DIR="${HERMES_DEBUG_HOME:-/tmp/hermes-debug-home}"
CDP_PORT="${CDP_PORT:-9333}"
MOCK_PORT=53999
VITE_PORT=5174
ELECTRON="$DESKTOP/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron"

mkdir -p "$HOME_DIR"
cat > "$HOME_DIR/config.yaml" <<YAML
model: { default: mock-model, provider: mock }
providers:
  mock: { api: http://127.0.0.1:$MOCK_PORT/v1, name: Mock, api_mode: chat_completions,
          key_env: MOCK_API_KEY, models: { mock-model: {} }, context_length: 4096 }
YAML
echo "MOCK_API_KEY=debug" > "$HOME_DIR/.env"

# 1. mock inference server (SSE streamer)
( node -e '
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
s.listen('"$MOCK_PORT"',"127.0.0.1",()=>console.log("mock inference on '"$MOCK_PORT"'"));
' ) &

# 2. vite renderer
( cd "$DESKTOP" && npm run dev:renderer ) &

sleep 6
# 3. electron against isolated home, with CDP
( cd "$DESKTOP" && \
  HERMES_HOME="$HOME_DIR" \
  HERMES_DESKTOP_PYTHON="$REPO/.venv/bin/python" \
  HERMES_DESKTOP_CDP_PORT="$CDP_PORT" \
  HERMES_DESKTOP_DEV_SERVER="http://127.0.0.1:$VITE_PORT" \
  HERMES_DESKTOP_USER_DATA_DIR=/tmp/cdp-probe-userdata \
  HERMES_DESKTOP_IGNORE_EXISTING=1 \
  "$ELECTRON" . --user-data-dir=/tmp/cdp-probe-userdata ) &

sleep 5
echo "=== Now start the MCP server in another process: ==="
echo "cd $DESKTOP/mcp && npm install"
echo "DESKTOP_DEBUG_MCP_ALLOW_ACT=1 DESKTOP_DEBUG_MCP_EXPECTED_HOME=$HOME_DIR DESKTOP_DEBUG_MCP_PORT=$CDP_PORT node server.mjs"
wait
