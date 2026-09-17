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
