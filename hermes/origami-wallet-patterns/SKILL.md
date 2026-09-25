---
name: origami-wallet-patterns
description: Find origami leather wallet patterns.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [leather, origami, wallet, pattern, fold-cut, no-sew]
    category: creative
    related_skills: [leatherworking-patterns, wallet-pattern-lessons]
---

# Origami Wallet Patterns Skill

Find, validate, and analyze origami-style leather wallet patterns that use a single piece of leather with no stitching, relying on folding and precise cutting for functionality.

## When to Use

- User wants a wallet made from one piece of leather without seams
- Design is fold-and-cut (origami) style, not sewn
- Wallet should function as a bifold (folding in half)
- User accepts or prefers minimal/no hardware (snaps optional)
- Pattern must be downloadable (PDF, SVG, or image)

## Workflow

### 1. Identify Pattern Requirements
- **Form factor**: Confirm user wants bifold (not trifold, not cardholder only)
- **Hardware**: Ask if user wants snap/rivet installation or prefers fold-only
- **Size**: Request target dimensions (e.g., fits 10+ cards, specific currency bills)
- **Leather thickness**: Most work best with 1.2-2.0mm veg-tan cowhide

### 2. Search and Collect Patterns

**Free patterns (always check availability first):**
- **CraftiveThink / LEATHER RIOT**: Minimalist Stitchless Origami Wallet
  - One piece, 308×220 mm, folds to bifold with 4 diagonal slits as "locks"
  - No snap holes (optional), no sewing lines
  - Download: https://craftivethink.com/minimalist-stitchless-leather-wallet.html
  - **Video tutorial**: https://www.youtube.com/watch?v=Vu4QEZ7j_5s
  - Validate by downloading PDF and rendering with pymupdf

- **GlienDesign "Origami inspired by Lemur"**
  - Video: https://www.youtube.com/watch?v=syhgmSuSek0
  - Often includes Google Drive link (validate if accessible)
  - If GDrive link broken, search for alternative mirrors or repos

**Premium patterns (Etsy and specialty sites):**
- **No-Stitch Leather Bifold Wallet** (Etsy)
  - PDF + SVG, includes video tutorial
  - Search: "etsy 1575698334 no-stitch bifold wallet pattern"

- **No Stitch Bundle** (Etsy)
  - Multiple patterns: bifold + cardholder + long wallet
  - Search: "etsy 4309235183 no-stitch leather wallet pattern bundle"

- **Leather Origami Card Wallet** (Etsy)
  - PDF + SVG, no-stitch cardholder
  - Search: "etsy 1129314112 leather origami card wallet pattern"

- **Olive Sparrow W3 Origami Wallet**
  - Premium PDF pattern from known leather pattern designer
  - Website: https://olivesparrowcrafts.com/store/p/w3-origami-wallet-pdf-pattern

### 3. Validate Pattern Authenticity

**Mandatory checks for all patterns:**
- **Single piece contour**: No separate panels, no cut lines for sewing
- **Fold lines**: Usually dashed or indicated by scoring marks
- **No sewing holes**: Absence of stitch guide dots
- **Functional folds**: Must create pockets through geometry alone
- **Size compatibility**: Check if pattern fits standard cards/bills

**Validation tools:**
- Download PDF and convert to PNG with pymupdf
- Use vision_analyze to identify:
  - Single-piece contour (no separate panels)
  - Fold lines (dashed/dotted lines or scoring marks)
  - Button/rivet holes (if present)
  - Diagonal slits ("locks" for origami mechanism)
  - Overall dimensions
- Verify 1:1 scale with pixel measurements

### 4. Pattern Analysis Report

For each validated pattern, provide:

**Basic Info:**
- Pattern name and source
- Designer/author
- Price (free vs premium)
- Format (PDF, SVG, image)

**Design Features:**
- Single piece dimensions (e.g., 308×220 mm)
- Fold mechanism (number and type of folds)
- Pocket creation method (diagonal slits, tongue-and-groove)
- Hardware requirements (snaps, rivets, or none)
- Card capacity estimate
- Bill compatibility

**Pros/Cons:**
- Advantages (simplicity, no sewing required)
- Limitations (card security, thickness limits)
- Skill level required (folding precision, leather selection)

**Fabrication Notes:**
- Recommended leather thickness (typically 1.2-2.0mm veg-tan)
- Cutting tools needed (craft knife, ruler, cutting mat)
- Folding technique (bone folder recommended)
- Optional hardware installation guide

### 5. Pattern Comparison

When multiple patterns are found, compare:

| Feature | CraftiveThink | GlienDesign | Premium Etsy | Olive Sparrow |
|---------|---------------|-------------|--------------|---------------|
| Price | Free | Free | $5-15 | $8-12 |
| Format | PDF | Video+PDF | PDF+SVG | PDF |
| Size | 308×220 mm | Varies | Varies | Varies |
| Folds | 3 main + 2 diagonal | Similar | Similar | Similar |
| Hardware | Optional snaps | Optional | Optional snaps | Optional |
| Tutorial | Video | Video | Video | Written |
| Skill Level | Beginner | Beginner | Intermediate | Intermediate |

## Pitfalls

- **Broken download links**: Free patterns often have dead GDrive links. Always check accessibility and provide alternative sources or mirrors.
- **Misleading descriptions**: Some "origami" patterns still use hidden stitching. Verify by examining the actual pattern file, not just descriptions.
- **Scale errors**: Free patterns may not be true 1:1. Always validate dimensions by rendering and measuring.
- **Missing instructions**: Origami patterns require precise folding techniques. Look for video tutorials or detailed written instructions.
- **Hardware confusion**: Some patterns include snap holes but no instructions. Clarify if user has snap tools or prefers fold-only.
- **Leather thickness limits**: Origami wallets work best with thin leather (1.2-2.0mm). Thicker leather may not fold cleanly.
- **Pattern authenticity**: Verify that "single piece" patterns aren't actually multiple panels disguised as one.

## Quality Gates

- **Pattern must be downloadable**: No screenshots or descriptions only
- **Must function as bifold**: Trifold or cardholder-only designs don't qualify
- **No sewing required**: The folding mechanism must create functional pockets
- **Real-world validation**: Pattern should be used by others (check comments, reviews)

## Related Skills

- `leatherworking-patterns`: For traditional sewn wallet patterns
- `wallet-pattern-lessons`: For detailed sewing pattern construction rules
- `pdf`: For pattern file validation and conversion

## Pattern Sources Database

See `references/validated-patterns.md` for a comprehensive list of verified free and premium origami wallet patterns, including download links, validation status, and common issues encountered.

## Example Validation Workflow

```python
# Download and validate CraftiveThink pattern
import urllib.request
import pymupdf
from hermes_tools import vision_analyze

download_pdf("https://craftivethink.com/minimalist-stitchless-leather-wallet.html")
doc = pymupdf.open("pattern.pdf")
png_path = "pattern.png"
doc[0].get_pixmap(dpi=110).save(png_path)

# Analyze with vision
analysis = vision_analyze(png_path, "Describe the origami wallet pattern: single piece? fold lines? diagonal slits? dimensions? hardware holes?")
print(analysis)
```

## Pattern Sources to Monitor

- **Etsy**: Search for "origami wallet", "no stitch wallet", "fold wallet"
- **YouTube**: GlienDesign, CraftiveThink, leatherworking channels
- **Specialty sites**: Olive Sparrow Crafts, Tandy Leather, Sailrite
- **GitHub**: Search for origami wallet pattern repositories
- **Reddit**: r/myog (make your own gear), r/leatherworking
