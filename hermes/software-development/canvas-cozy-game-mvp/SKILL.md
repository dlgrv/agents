---
name: canvas-cozy-game-mvp
description: "Use when building single-file Canvas game MVPs."
---
# Canvas game MVP

- Keep editable source sections and concatenate into one standalone HTML. Syntax-check the concatenation to catch duplicate globals.
- Define contracts before parallel work: player footprint, numeric tool index vs tool name, seed selection, world arrays, indoor coordinates, render time units.
- Require coding subagents to return actual artifact paths and test output. Verify existence; design prose does not prove implementation.
- Use node:test VM harnesses with minimal DOM/Canvas stubs to test real simulation: growth, energy no-ops, terrain/object persistence, fishing, daily gifts, collisions.
- Run actual Chrome with Playwright in an isolated profile. Drive farm actions, sleep and sale through keyboard/mouse, collect pageerrors, reload saved progress. Position setup is not a pathfinding test.
- If browser helper blocks localhost, use local Playwright and installed Chrome; do not expose the server publicly or attach to user's active browser.
- Inspect screenshots. Reduce grass noise and put hint text on contrasting panels.
- Deliver standalone HTML and loopback URL; viewport-filling games may not size properly in inline preview frames.
- State scope honestly: collecting wood without crafting is not a crafting system; guests without room management are not an inn simulation.
- Resolution upgrades (user asks for more texture detail): keep logic in logical pixels, add a SCALE constant, and upgrade art at three distinct layers — procedural tiles/props repaint native at 4x with painter contexts setTransform(SCALE...), matrix sprites multiply each pixel by SCALE into a w*SCALE canvas, and UI/logical overlays keep 1x coordinates via a blit(img,x,y) that divides native size by SCALE. Beware double-scaling when a blanket regex already multiplied canvas dims; verify with an art test asserting SPR.house.width === logical*SCALE.
- Mixed pixel densities read as noise after scaling: tile speckle grain should be 2-4 native px with lower contrast, matching sprite pixel size; verify with a screenshot review pass.
- When unit tests break after core changes, read the exact failure (often just missing canvas stub methods like setTransform in the test harness) before touching game code.
