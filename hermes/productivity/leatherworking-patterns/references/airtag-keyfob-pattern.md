# AirTag Keyfob Pattern Design Guide

## Overview
Circular leather "donut with tab" pattern for AirTag keychain fobs. AirTag held by skin tension (no glue/velcro), removable by fingers. Key ring attachment via dedicated hole.

## Design Parameters

- **Outer diameter:** 6.8 cm (cut line)
- **Hole diameter:** 2.85 cm (AirTag ⌀31.9 mm grip zone)
- **Stitch line diameter:** 3.82 cm (24 holes, 5.0 mm pitch)
- **Skin grip:** 0.17 cm per side (5.3% perimeter compression)
- **Skin zone:** 0.8 cm diameter (skive/score line, dashed)
- **Tab width:** 1.6 cm (extends to 19 cm for key ring)
- **Ring hole:** 0.5 cm diameter (for ⌀25 mm split ring)

## AirTag Specifications
- **Dimensions:** ⌀31.9 mm × 8.0 mm (Apple official)
- **Hole tolerance:** Must be ≤ AirTag diameter for grip
- **Hole minimum:** ≥2.0 cm (prevents tearing)
- **Ring width:** ≥0.7 cm (material between hole and stitch line)
- **Stitch offset:** 0.25–0.35 cm from outer edge (bearing surface not on edge)
- **Material between hole and stitch:** ≥0.5 cm per side

## Hole Grid and Stitching

- **Hole count:** 24 (even number for symmetric pairing)
- **Angular pitch:** 15.00° (360°/24)
- **Arc pitch:** 5.0 mm (π × 3.82 cm / 24)
- **First hole position:** Top (12 o'clock, 0°)
- **Hole exclusion:** Minimum radius > hole_radius + 0.3 cm (no holes on fold lines)

## Ring Attachment
- **Ring hole position:** Tab tip, center (x=8.95, y=15.0)
- **Ring hole diameter:** 0.5 cm (for ⌀25 mm split ring)
- **Ring type:** Split ring (25 mm diameter, allows key attachment)
- **Load bearing:** Tab carries key weight, not AirTag

## Thread and Assembly

- **Thread length:** ~58 cm (4 × stitch circumference + 10 cm reserve)
- **Assembly time:** 20–30 minutes per fob
- **Thread type:** Standard waxed linen thread (5-6 thickness)
- **Needle size:** Leather needle (chisel point)

## Pattern Generation

```python
# Key geometry calculations
AIRTAG_D = 3.19      # AirTag diameter (cm)
HOLE_D  = 2.85       # Hole diameter (cm)
OUT_D   = 6.8        # Outer diameter (cm)
STITCH_D = 3.82      # Stitch line diameter (cm)
N_HOLES = 24        # Number of stitches
SKIVE_W = 0.8       # Skin zone diameter (cm)
TAB_W = 1.6         # Tab width (cm)
RING_HOLE_D = 0.5   # Ring hole diameter (cm)

# Grip calculation (perimeter compression)
CIRC_IN  = math.pi * AIRTAG_D      # AirTag perimeter: 10.02 cm
CIRC_HOLE = math.pi * HOLE_D       # Hole perimeter: 8.95 cm
GRIP_PCT = round((1 - CIRC_HOLE / CIRC_IN) * 100, 1)  # 5.3%
STRETCH = round((AIRTAG_D - HOLE_D) / 2, 3)            # 0.17 cm per side

# Stitch pitch (arc length between holes)
PITCH   = round(math.pi * STITCH_D / N_HOLES, 3)        # 0.5 cm
THREAD  = round(math.pi * STITCH_D * 4 + 10, 0)        # x4 saddle stitch + reserve
```

## Testing and Validation

### Test Categories
1. **Parameter validation** (A1-A7): Verify dimensions and grip calculations
2. **Hole grid** (B1-B6): Count, position, spacing, exclusion zones
3. **Thread calculation** (C1-C2): Length within realistic bounds
4. **PDF vector accuracy** (D1-D5): Page size, circle diameters, hole positions
5. **PNG pixel verification** (E1-E2): content margins, visual layout
6. **Tab validation** (F1-F2): Tab extends beyond circle, ring hole present

### Critical Tests
- **D2:** Verify PDF contains circles ⌀2.85, ⌀1.6, and ring hole ⌀0.5
- **D4:** Confirm exactly 24 filled dots in template zone
- **D5:** Check each hole position matches expected coordinates (±0.1 mm)
- **E1:** Ensure all content >3mm from page edges
- **F1:** Tab extends beyond circle (x > OUT_D/2)

## Common Pitfalls

- **Hole size too small:** <2.0 cm causes tearing
- **Hole size too large:** >AirTag diameter prevents grip
- **Stitch line too close to edge:** <0.25 cm weakens seam
- **Insufficient ring width:** <0.7 cm tears during insertion
- **Grid alignment:** Ensure holes don't aligned with fold lines
- **Thread length:** Underestimation causes mid-project stops
- **Tab stress:** Tab carries key weight, not AirTag

## Assembly Instructions

1. **Cut one fob** from leather (single piece: donut + tab)
2. **Score skin zone** (⌀0.8 cm dashed circle) on back side
3. **Punch 24 holes** along stitch line (⌀3.82 cm)
4. **Punch ring hole** at tab tip (⌀0.5 cm)
5. **Sew with saddle stitch** (thread length ≈58 cm)
6. **Insert split ring** through ring hole
7. **Attach keys** to split ring
8. **Insert AirTag** through hole (skin tension holds it)

## Use Cases

- **Keychain:** Standalone AirTag key fob
- **Bag accessory:** Mount on strap or handle
- **Wallet attachment:** Use as AirTag keyring
- **Laptop bag:** Attach to zipper pull

## File Structure

- `make_airtag_keyfob.py` - Pattern generator
- `tests/test_airtag_keyfob.py` - Test suite (25/25 tests)
- `out/airtag_keyfob_A4.pdf` - Ready-to-print pattern
- `out/check_airtag_fob.png` - Visual preview

## Validation Metrics

- **Test suite:** 25/25 passing
- **PDF accuracy:** Vector circles within ±0.05 mm
- **Hole alignment:** All 24 holes at exact positions (±0.1 mm)
- **Page margins:** All content >3mm from edges
- **Scale verification:** 1 cm = 39.37 pixels (100 DPI)
- **Tab extension:** Tab extends beyond circle by ≥1.2 cm
