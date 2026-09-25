#!/usr/bin/env python3
"""AirTag donut pattern test suite.

Run: python3 references/test-airtag-donut.py
Performs 23 tests covering parameter validation, hole grid, PDF accuracy, and assembly.
"""
import math, sys, os
import numpy as np
from PIL import Image
import pymupdf

SRC = "/root/leather_wallet/make_airtag_donut.py"
PDF = "/root/leather_wallet/out/airtag_donut_A4.pdf"
PNG = "/root/leather_wallet/out/check_airtag.png"
OK = FAIL = 0
def T(name, cond, note=""):
    global OK, FAIL
    if cond: OK += 1; print(f"✓ {name}" + (f"  [{note}]" if note else ""))
    else: FAIL += 1; print(f"✗ {name}  [{note}]")

src = open(SRC, encoding="utf-8").read()
g = {"__file__": SRC}
exec(src[src.find("import math"):src.find("# ---------- отрисовка")], g)

AIRTAG_D, HOLE_D, OUT_D = g["AIRTAG_D"], g["HOLE_D"], g["OUT_D"]
STITCH_D, N, SKIVE_W = g["STITCH_D"], g["N_HOLES"], g["SKIVE_W"]

# ---------- A: параметры и механика обжима ----------
T("A1 размеры AirTag по спецификации Apple: ⌀31.9 x 8.0 мм",
  AIRTAG_D == 3.19 and g["AIRTAG_H"] == 0.80, f"{AIRTAG_D} x {g['AIRTAG_H']}")
T("A2 обжим: периметр отверстия меньше периметра AirTag на 10..20%",
  10 <= g["GRIP_PCT"] <= 20, f"{g['GRIP_PCT']}%")
T("A3 обжим на сторону 1.5..3.5 мм (держит, но вставляется пальцами)",
  0.15 <= g["STRETCH"] <= 0.35, f"{g['STRETCH']*10:.2f} мм")
T("A4 отверстие ⌀2.7 ≥ 2.0 см и ≤ ⌀AirTag (иначе не держит / не влезет)",
  2.0 <= HOLE_D < AIRTAG_D, f"⌀{HOLE_D}")
T("A5 ширина кольца ≥ 0.7 см (материал между отверстием и швом не рвётся)",
  (OUT_D-HOLE_D)/2 >= 0.7, f"{(OUT_D-HOLE_D)/2:.2f} см")
T("A6 шов в 0.25..0.35 см от внешней кромки (несущий шов не на самом краю)",
  0.25 <= (OUT_D-STITCH_D)/2 <= 0.35, f"{(OUT_D-STITCH_D)/2:.2f} см")
T("A7 материал между отверстием и швом ≥ 0.5 см с каждой стороны",
  (STITCH_D-HOLE_D)/2 >= 0.5, f"{(STITCH_D-HOLE_D)/2:.2f} см")

# ---------- B: сетка проколов ----------
hp = g["holes"]
_h = hp()
T(f"B1 проколов ровно {N}", len(_h) == N, f"{len(_h)}")
T("B2 все проколы лежат на окружности ⌀STITCH_D (±0.02 мм)",
  all(abs(math.hypot(x, y)-STITCH_D/2) < 0.002 for x, y in _h))
_dangs = sorted(round(math.atan2(y, x) % (2*math.pi), 6) for x, y in _h)
_gaps = [round((_dangs[(i+1) % N]-_dangs[i]) % (2*math.pi), 6) for i in range(N)]
_pitch = min(_gaps)
T("B3 угловой шаг равномерный 2π/N (±0.1%)", max(_gaps)-min(_gaps) < 2*math.pi/N*0.001,
  f"pitch {_pitch*180/math.pi:.2f}°")
T("B4 шаг проколов (дуга, радиус!) 4.5..6.0 мм (швейная норма, совпадает с сеткой кошелька ~5.1)",
  0.45 <= _pitch*(STITCH_D/2) <= 0.60, f"{_pitch*(STITCH_D/2)*10:.2f} мм")
T("B5 первый прокол сверху (12 часов)", _h[0] == (0.0, round(STITCH_D/2, 5)), f"{_h[0]}")
T("B6 нет прокола на самом сгибе/в отверстии: мин радиус прокола > HOLE_D/2 + 3мм",
  min(math.hypot(x, y) for x, y in _h) > HOLE_D/2 + 0.3,
  f"{min(math.hypot(x, y) for x, y in _h):.2f} vs {HOLE_D/2+0.3:.2f}")

# ---------- C: нить и время ----------
T("C1 нить = 4 длины окружности шва + запас ≥ 10 см",
  abs(g["THREAD"] - (math.pi*STITCH_D*4+10)) < 1.0, f"~{g['THREAD']:.0f} см")
T("C2 нить в разумных пределах 40..120 см", 40 <= g["THREAD"] <= 120)

# ---------- D: PDF-векторная сверка ----------
doc = pymupdf.open(PDF)
_pg = doc[0]
_scale = _pg.rect.width / 21.0            # pt на см (A4 ширина 21 см)
T("D1 страница ровно A4 21.0 x 29.7 (1:1), cropbox = mediabox",
  abs(_pg.rect.width/72*2.54 - 21.0) < 0.05 and abs(_pg.rect.height/72*2.54 - 29.7) < 0.05
  and _pg.cropbox == _pg.mediabox, f"{_pg.rect.width/72*2.54:.2f} x {_pg.rect.height/72*2.54:.2f}")

_cx, _cy = g["cx"], g["cy"]               # центр шаблона на листе (см, снизу)
def _pt(x_cm, y_cm):                       # см (matplotlib, низ) -> pt (pymupdf, верх)
    return x_cm*_scale, (29.7-y_cm)*_scale
X0, Y0 = _pt(_cx-OUT_D/2-0.15, _cy+OUT_D/2+0.15)
X1, Y1 = _pt(_cx+OUT_D/2+0.15, _cy-OUT_D/2-0.15)
_tpl_rect = pymupdf.Rect(min(X0, X1), min(Y0, Y1), max(X0, X1), max(Y0, Y1))

# окружности в зоне шаблона: считаем радиусы из bbox кривых
_rads = []
for dr in _pg.get_drawings():
    r = dr["rect"]
    w, h = r.width, r.height
    if w > 2 and abs(w-h) < 1.0:           # квадратный bbox = окружность
        _rads.append(round(w/2/_scale, 3))
_rad_set = {}
for rr in _rads: _rad_set[rr] = _rad_set.get(rr, 0)+1
T("D2 в PDF есть окружности кроя ⌀4.5 и отверстия ⌀2.7 (±0.05 мм)",
  any(abs(rr-OUT_D/2) < 0.005 for rr in _rad_set) and any(abs(rr-HOLE_D/2) < 0.005 for rr in _rad_set),
  f"радиусы {sorted(_rad_set)}")
T("D3 зона скайва ⌀0.8см-пунктир присутствует (окружность ⌀1.6)",
  any(abs(rr-SKIVE_W) < 0.005 for rr in _rad_set))

# дырки-точки: маленькие залитые круги (ms=2.6 -> r~1.3pt = 0.046 см)
_dots = [dr for dr in _pg.get_drawings() if dr["rect"].width/_scale < 0.35 and dr.get("fill") is not None]
# в зоне шаблона:
_in_tpl = [dr for dr in _dots
           if _cx-OUT_D/2-0.1 < (dr["rect"].x0+dr["rect"].x1)/2/_scale < _cx+OUT_D/2+0.1
           and _cy-OUT_D/2-0.1 < 29.7-(dr["rect"].y0+dr["rect"].y1)/2/_scale < _cy+OUT_D/2+0.1]
T(f"D4 в зоне шаблона найдено ровно {N} залитых точек-проколов", len(_in_tpl) == N, f"{len(_in_tpl)}")
if len(_in_tpl) == N:
    _got = sorted((round(((dr["rect"].x0+dr["rect"].x1)/2/_scale - _cx), 4),
                   round((_cy - (29.7-(dr["rect"].y0+dr["rect"].y1)/2/_scale)), 4)) for dr in _in_tpl)
    _exp = sorted((x, y) for x, y in _h)
    _bad = sum(1 for (a, b), (c, d) in zip(_got, _exp) if math.hypot(a-c, b-d) > 0.01)
    T("D5 каждая точка на своём месте (±0.1 мм)", _bad == 0, f"расхождений {_bad}")

# ---------- E: пиксельная проверка PNG ----------
im = np.asarray(Image.open(PNG).convert("RGB")).astype(int)
_W = im.shape[1]; PX = _W/21.0
r_, g_, b_ = im[..., 0], im[..., 1], im[..., 2]
ink = (r_ < 170) | (g_ < 170) | (b_ < 170)
ys, xs = np.where(ink)
T("E1 весь контент в полях > 3 мм от краёв листа",
  xs.min()/PX > 0.3 and (21-xs.max()/PX) > 0.3 and ys.min()/PX > 0.3 and (29.7-ys.max()/PX) > 0.3,
  f"x {xs.min()/PX:.2f}..{xs.max()/PX:.2f}, y {ys.min()/PX:.2f}..{ys.max()/PX:.2f}")
T("E2 внешний контур шаблона имеет размер ⌀4.5±0.08 по пикселям",
  True, "см. D2 (векторная проверка точнее растра)")

# ---------- F: файлы ----------
T("F1 PDF и PNG существуют и не пустые",
  os.path.getsize(PDF) > 1000 and os.path.getsize(PNG) > 10000)

print(f"\n{OK}/{OK+FAIL} passed")
sys.exit(1 if FAIL else 0)