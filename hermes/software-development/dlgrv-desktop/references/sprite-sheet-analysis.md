# Measuring sprite frame boundaries in a PNG (sips → BMP → raw pixels)

macOS has no PIL by default, and `execute_code`/`terminal` heredocs get blocked by the
command parser. The working pipeline: convert the PNG to BMP with `sips` (BMP is
uncompressed, trivially parseable with `struct`), then parse alpha/color columns with
plain Python via `execute_code`.

## Pipeline

```bash
sips -s format bmp sprite.png --out /tmp/sprite.bmp
```

```python
from struct import unpack
data = open('/tmp/sprite.bmp','rb').read()
off = unpack('<I', data[10:14])[0]
w = unpack('<i', data[18:22])[0]
h = abs(unpack('<i', data[22:26])[0])   # BMP height is negative for top-down
bpp = unpack('<H', data[28:30])[0]      # sips emits 32bpp BGRA
row = ((w*4)+3)//4*4
px = data[off:]

def solid(x, y):  # BMP rows are bottom-up
    i = (h-1-y)*row + x*4
    b,g,r = px[i], px[i+1], px[i+2]
    return not (b==0 and g==0 and r==0)

# column occupancy profile: count of solid pixels per column
for x in range(x0, x1, 8):
    c = sum(1 for y in range(0, h, 1) if solid(x, y))
    print(x, c, '#'*(c//4))
```

## Why: the dino sprite lesson

The Chrome dino 2x sprite sheet (`offline-sprite-2x.png`, 2404×130) documents frame
offsets in **LDPI pixels** in the original JS (`TREX: {x:1678,y:2}`, frames
`RUNNING: [88, 132]`). Multiplying those by 2 (→176, 264) produced **torn sprites** —
the frame landed between real frames.

Column-occupancy profiling showed frames actually sit at ~92px steps in the 2x sheet.
Fix: use measured 2x offsets directly (`RUNNING: [184, 276]`) and do NOT multiply.

Lesson: **never trust documented offsets across sprite scale variants — measure the
actual sheet.** The profile printout (count histogram per column) makes frame gaps
obvious: real frames are dense plateaus separated by near-zero columns.

## Tips

- BMP rows are bottom-up: screen y maps to `(h-1-y)*row`.
- sips BMP is 32bpp BGRA, compression 3 (bitfields) — alpha at byte +3.
- Crop a region for visual inspection: `sips -c <h> <w> --cropOffset <y> <x> in.png --out out.png`.
- Verify visually with `vision_analyze` on the crop AND the in-game screenshot; a
  torn frame looks like "sprite split into two pieces".
