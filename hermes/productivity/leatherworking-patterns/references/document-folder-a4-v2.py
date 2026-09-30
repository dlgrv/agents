# -*- coding: utf-8 -*-
"""Папка-конверт A4 v2: ОДИН кусок кожи, сгиб снизу, шов по 2 боковым сторонам.

Аудит v1: интерьер 21.8 не вмещал 200 листов (нужно 23.0). v2 кроится под
200 листов 80 г/м2 (стопка 2.0 см).

Конструкция:
- плоский крой ОДНОЙ деталью 24.3 x 69.4: [вход+передняя 31.7][СГИБ y=31.7]
  [задняя 31.7 + клапан 6.0];
- сгиб снизу готовой папки (линия y=31.7 на чертеже) — не сшивается;
- шов: 4 сегмента (2 на борт: передняя от входа до сгиба, задняя от сгиба до
  основы клапана). Клапан, вход и свободная кромка клапана НЕ сшиваются;
  наборы дырок передней и задней совпадают 1:1 при сложении (зеркально от сгиба);
- вход (кромка y=0 чертежа): верхние углы ПРЯМЫЕ 90°, выемка под пальцы
  по центру (прогиб ВНУТРЬ кожи, глубина 6 мм, проём 24 мм);
- кнопка 15 мм на клапане (2.5 от свободной кромки), ответная на передней
  (3.5 от входа) — при закрытии совпадают.

Посадка: интерьер ширина 23.2 (лист 21.0 + стопка 2.0 + воздух 0.2);
глубина от сгиба 30.6 (листы 29.7 — утоплены, клапан накрывает стопку ~4 см).
Лист чертежа 42 x 76 см, масштаб 1:1 (39.37 px/см).
"""
import math, os, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, Rectangle
from matplotlib.lines import Line2D

OUT = "/root/leather_docs/out_v2"
os.makedirs(OUT, exist_ok=True)

# ---------- параметры (см) ----------
A4_W, A4_H   = 21.0, 29.7
STACK        = 2.0     # 200 листов 80 г/м2 (0.1 мм/лист)
AIR          = 0.2
DEDUCT       = 1.10    # 2x(шов 4мм + толщина кожи)
INT_W        = round(A4_W + STACK + AIR, 2)     # 23.2
PW           = round(INT_W + DEDUCT, 2)         # 24.3
PH           = 31.7    # передняя и задняя панели (от сгиба до входа)
INT_H        = round(PH - DEDUCT, 2)            # 30.6
FLAP         = 6.0     # клапан вверх от задней кромки
TOTAL_H      = round(PH + PH + FLAP, 2)         # 69.4
FLAP_BASE    = round(TOTAL_H - FLAP, 2)         # 63.4 (перегиб клапана)
EDGE         = 0.40
STEP         = 0.50
R            = 1.50    # только углы клапана R15 (вход — прямые, сгиб — сквозной борт)
NOTCH_D      = 0.60
NOTCH_W      = 2*math.sqrt(R*R - (R-NOTCH_D)**2)          # 2.4
RHO          = (NOTCH_W**2/4 + NOTCH_D**2) / (2*NOTCH_D)  # 1.5
ALPHA        = math.degrees(math.asin((NOTCH_W/2)/RHO))   # 53.13°
BTN_D        = 2.5     # кнопка от свободной кромки клапана
BTN_Y        = round(TOTAL_H - BTN_D, 2)        # 66.9 на чертеже
MATE_Y       = round(BTN_Y - FLAP_BASE, 2)      # 3.5 над входом (совпадает при закрытии)

def arc_pts(cx, cy, r, a0, a1, n=36):
    return [(cx + r*math.cos(math.radians(a0 + (a1-a0)*k/n)),
             cy + r*math.sin(math.radians(a0 + (a1-a0)*k/n))) for k in range(n+1)]

def outline_flat():
    """Плоский крой: обход CCW от левого борта на сгибе. Вход y=0 (углы прямые,
    выемка прогибом вверх), сгиб y=31.7 — борт сквозной без углов, клапан
    сверху (углы R15)."""
    pts = [(0.0, PH)]                                           # сгиб, левый борт
    pts += [(0.0, TOTAL_H - R)]                                 # левый борт вверх
    pts += arc_pts(R, TOTAL_H - R, R, 180, 90)[1:]              # угол клапана левый
    pts += [(PW - R, TOTAL_H)]                                  # свободная кромка
    pts += arc_pts(PW - R, TOTAL_H - R, R, 90, 0)[1:]           # угол клапана правый
    pts += [(PW, PH)]                                           # правый борт, вершина сгиба
    pts += [(PW, 0)]                                            # правый борт до входа
    pts += [(PW/2 + NOTCH_W/2, 0)]                              # вход к выемке
    pts += arc_pts(PW/2, NOTCH_D - RHO, RHO, 90 - ALPHA, 90 + ALPHA, n=24)[1:]  # выемка
    pts += [(0.0, 0)]                                           # вход, левый угол
    pts += [pts[0]]                                             # замыкание по борту
    return pts

def seam_path():
    """4 сегмента (2 на борт): передняя от входа до сгиба, задняя от сгиба до
    перегиба клапана. Клапан и вход не сшиваются."""
    segs = []
    for x in (EDGE, PW - EDGE):
        segs.append([(x, EDGE), (x, PH - EDGE)])                # передняя
        segs.append([(x, PH + EDGE), (x, FLAP_BASE - EDGE)])    # задняя
    return segs

def punch(path, step=STEP):
    segs, total = [], 0.0
    for (x1,y1),(x2,y2) in zip(path, path[1:]):
        d = math.hypot(x2-x1, y2-y1)
        segs.append((x1,y1,x2,y2,d)); total += d
    n_div = max(2, round(total/step))
    n = n_div + 1
    holes, i, acc = [], 0, 0.0
    for k in range(n):
        target = total * k / n_div
        while acc + segs[i][4] < target:
            acc += segs[i][4]; i += 1
        x1,y1,x2,y2,d = segs[i]
        t = (target - acc)/d if d else 0
        holes.append((x1 + (x2-x1)*t, y1 + (y2-y1)*t))
    return holes, total, n

BLUE, PALE, MUTE = "#1144cc", "#7aa3e8", "#888888"

def check_strip(ax, x0, y0, fs=6.5):
    ax.plot([x0, x0+10],[y0,y0], color="black", lw=0.8, zorder=6)
    for xx in (x0, x0+10):
        ax.plot([xx,xx],[y0-0.25,y0+0.25], color="black", lw=0.8, zorder=6)
    ax.text(x0+5, y0-0.32, "проверь линейкой: ровно 10.0 см", fontsize=fs,
            ha="center", va="top", zorder=6)

def scale_of(ax):
    p0 = ax.transData.transform((0,0)); p1 = ax.transData.transform((1,0))
    return round(float(p1[0]-p0[0]), 2)

def dim(ax, x1, y1, x2, y2, label, vertical=False, lx=None, ly=None):
    ax.add_line(Line2D([x1,x2],[y1,y2], color="black", lw=0.7))
    for (x,y) in ((x1,y1),(x2,y2)):
        seg = (Line2D([x-0.6,x+0.6],[y,y]) if not vertical
               else Line2D([x,x],[y-0.6,y+0.6]))
        seg.set(color="black", lw=0.7)
        ax.add_line(seg)
    tx = lx if lx is not None else (x1+x2)/2
    ty = ly if ly is not None else (y1+y2)/2 + (0.35 if not vertical else 0)
    ax.text(tx, ty, label, fontsize=9, ha="center",
            va="bottom" if not vertical else "center",
            rotation=90 if vertical else 0)

# ================= лист 42.0 x 76.0, 1:1 =================
LW, LH = 42.0, 76.0
fig = plt.figure(figsize=(LW/2.54, LH/2.54), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(-3.0, 39.0); ax.set_ylim(-3.4, 72.6)
ax.set_aspect("equal"); ax.axis("off")

ax.add_patch(Polygon(outline_flat(), closed=True, facecolor="none",
                     edgecolor="black", lw=1.6, zorder=2))

tot_holes = 0
for path in seam_path():
    holes, total, n = punch(path)
    tot_holes += n
    ax.plot([p[0] for p in path], [p[1] for p in path], color=PALE, lw=0.5, alpha=0.6, zorder=4)
    ax.plot([h[0] for h in holes], [h[1] for h in holes], ls="none",
            marker="o", ms=2.0, mfc=BLUE, mec=BLUE, zorder=5)

# линии сгибов
ax.plot([0.2, PW-0.2], [PH, PH], color=MUTE, lw=1.1, ls=(0, (7, 3)), zorder=3)
ax.text(PW/2, PH+0.55, "СГИБ папки (не сшивать, не резать)", fontsize=8, ha="center", color=MUTE)
ax.plot([0.2, PW-0.2], [FLAP_BASE, FLAP_BASE], color=MUTE, lw=0.9, ls=(0, (4, 3)), zorder=3)
ax.text(PW/2, FLAP_BASE+0.5, "перегиб клапана (скайв 1 см с изнанки)", fontsize=7, ha="center", color=MUTE)

# кнопка (на клапане) и ответная (на передней)
ax.add_patch(Circle((PW/2, BTN_Y), 0.18, facecolor="none", edgecolor="black", lw=1.3, zorder=6))
ax.text(PW/2+0.45, BTN_Y, f"кнопка 15 мм ({BTN_D} от свободной кромки)",
        fontsize=6.5, ha="left", va="center")
ax.add_patch(Circle((PW/2, MATE_Y), 0.18, facecolor="none", edgecolor=MUTE,
                    lw=1.0, ls=(0, (3, 2)), zorder=6))
ax.text(PW/2+0.45, MATE_Y, "ответная часть кнопки (при закрытии совпадает)",
        fontsize=6.5, ha="left", va="center", color=MUTE)

# выноска входа
ax.annotate("ВХОД (кромка y=0 = верх готовой папки):\nуглы прямые 90°, кромка без шва;\nвыемка под пальцы R15, глубина 6 мм",
            xy=(PW/2 + NOTCH_W/2, 0.15), xytext=(1.0, -3.2), fontsize=8, color=BLUE,
            va="bottom", arrowprops=dict(arrowstyle="->", color=BLUE, lw=1))

# размеры
dim(ax, 0, -1.15, PW, -1.15, f"{PW}", lx=PW/2)
dim(ax, -1.4, 0, -1.4, PH, f"{PH} (передняя)", vertical=True, lx=-2.6, ly=PH/2)
dim(ax, -1.4, PH, -1.4, FLAP_BASE, f"{PH} (задняя)", vertical=True, lx=-2.6, ly=(PH+FLAP_BASE)/2)
dim(ax, -1.4, FLAP_BASE, -1.4, TOTAL_H, f"{FLAP} (клапан)", vertical=True, lx=-2.6, ly=(FLAP_BASE+TOTAL_H)/2)
dim(ax, PW+0.9, FLAP_BASE, PW+0.9, TOTAL_H, f"{FLAP}", vertical=True, lx=PW+2.3, ly=(FLAP_BASE+TOTAL_H)/2)
check_strip(ax, 27, -2.0, fs=6)

ax.text(19, 72.2, "ПАПКА-КОНВЕРТ A4 v2 — ОДИН КУСОК 24.3 × 69.4, сгиб снизу, шов 2 борта — ЛЕКАЛО 1:1 — печать 100%",
        fontsize=10, weight="bold", ha="center", va="top")
scale = scale_of(ax)
fig.savefig(f"{OUT}/lechalo_A2plus_odin_kusok.pdf")
fig.savefig(f"{OUT}/check_flat.png", dpi=120)
plt.close(fig)

# ===== лист-приложение: контроль сборки (вид сложенной папки) =====
fig = plt.figure(figsize=(LW/2.54, LH/2.54), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(-3.0, 39.0); ax.set_ylim(-44.6, 8.6)
ax.set_aspect("equal"); ax.axis("off")
# задняя (сгиб y=0, вверх), передняя (вниз)
ax.add_patch(Rectangle((0, 0), PW, PH, facecolor="none", edgecolor=MUTE, lw=1.3, ls=(0, (5, 3)), zorder=2))
ax.add_patch(Rectangle((0, -PH), PW, PH, facecolor="none", edgecolor="black", lw=1.4, zorder=2))
ax.plot([0.2, PW-0.2], [0, 0], color=MUTE, lw=1.1, ls=(0, (7, 3)), zorder=3)
ax.text(PW/2, 0.8, "сгиб (низ папки)", fontsize=8, ha="center", color=MUTE)
# стопка листов
ax.add_patch(Rectangle((DEDUCT/2 + 0.1, -(0.52 + A4_H)), A4_W + STACK - 0.2, A4_H,
                       facecolor="#dde8ff", edgecolor="#1144cc", lw=1.0, zorder=1))
ax.text(PW/2, -(0.52 + A4_H/2), "A4 × 200\n(21.0 × 29.7, стопка 2.0)", fontsize=8,
        ha="center", va="center", color="#1144cc")
# клапан в ЗАКРЫТОМ виде (перегнут вниз поверх передней)
ax.add_patch(Rectangle((0, -FLAP), PW, FLAP, facecolor="none", edgecolor="black", lw=1.4, zorder=4))
ax.text(PW/2, -FLAP/2, "клапан 6.0 (закрыт) — накрывает стопку", fontsize=8, ha="center", va="center")
# кнопка/ответная совпали при закрытии
ax.add_patch(Circle((PW/2, -MATE_Y), 0.18, facecolor="none", edgecolor="black", lw=1.2, zorder=6))
ax.text(PW/2+0.45, -MATE_Y, "кнопка = ответная (совпали)", fontsize=7, ha="left", va="center")
dim(ax, PW+0.9, -PH, PW+0.9, 0, f"{PH} передняя", vertical=True, lx=PW+2.4, ly=-PH/2)
dim(ax, PW+0.9, 0, PW+0.9, PH, f"{PH} задняя", vertical=True, lx=PW+2.4, ly=PH/2)
ax.text(19, 7.5, "КОНТРОЛЬ СБОРКИ: вид сложенной папки (сгиб по центру)\nсиний = стопка A4 × 200; клапан показан закрытым",
        fontsize=9, weight="bold", ha="center", va="top")
fig.savefig(f"{OUT}/kontrol_sborki.pdf")
fig.savefig(f"{OUT}/check_folded.png", dpi=120)
plt.close(fig)

Lsum = sum(punch(p)[1] for p in seam_path())
summary = dict(PW=PW, PH=PH, FLAP=FLAP, TOTAL_H=TOTAL_H, FLAP_BASE=FLAP_BASE,
               INT_W=INT_W, INT_H=INT_H, n_holes=tot_holes,
               path_len=round(Lsum, 3), BTN=[PW/2, BTN_Y], MATE=[PW/2, MATE_Y])
with open(f"{OUT}/summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print("SCALE px/cm (must be 39.37):", {"flat": scale})
print(json.dumps(summary, ensure_ascii=False))
print("--- ПОСАДКА ---")
print(f"интерьер: {INT_W} x {INT_H} от сгиба")
print(f"ширина: лист+стопка {A4_W+STACK} -> запас {INT_W-A4_W-STACK:+.2f} (макс ~{int((INT_W-A4_W)*10/0.1)} листов 80 г/м2)")
print(f"глубина: листы 29.7, кромка входа на {INT_H} от сгиба -> утоплены {INT_H-A4_H:.1f}")
print(f"клапан: накрывает стопку на {FLAP-(INT_H-A4_H):.1f} см")
print(f"кнопка y={BTN_Y} ({BTN_D} от кромки клапана) | ответная на {MATE_Y} над входом -> при закрытии совпадают")
print(f"шов: 4 сегмента (2 борта), {tot_holes} проколов, путь {Lsum:.2f} см")
print(f"крой: {PW} x {TOTAL_H} — ОДИН кусок кожи")
print("saved:", OUT)