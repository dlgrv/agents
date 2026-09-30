# Тесты папки-конверта A4 v2 (один кусок, сгиб снизу). Standalone.
# Эталоны пересчитываются НЕЗАВИСИМО. Ключевой блок: посадка 200 листов.
import importlib.util, io, math, os, sys, contextlib, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom_utils import dist_seg, dist_circle  # noqa: E402

GEN = "/root/leather_docs/make_docs_folder_a4_v2.py"
_buf = io.StringIO()
spec = importlib.util.spec_from_file_location("docs2", GEN)
m = importlib.util.module_from_spec(spec)
sys.modules["docs2"] = m
with contextlib.redirect_stdout(_buf):
    spec.loader.exec_module(m)

OK = FAIL = 0
def T(name, cond, note=""):
    global OK, FAIL
    if cond: OK += 1; print(f"  ✓ {name}" + (f"  [{note}]" if note else ""))
    else: FAIL += 1; print(f"  ✗ {name}  [{note}]")

ol = m.outline_flat()

# ================= 1. ЕМКОСТЬ: 200 листов A4 =================
print("--- 1. Емкость: 200 листов A4 ---")
A4_W, A4_H = 21.0, 29.7
t80 = 0.10  # мм/лист 80 г/м2
need_w = A4_W + 200*t80/10                       # 23.0
T("ширина интерьер 23.2 >= лист+стопка 200x80г (23.0)",
  m.INT_W >= need_w, f"{m.INT_W} vs {need_w}, запас {m.INT_W-need_w:+.2f}")
T("запас по ширине >= 0.2", m.INT_W - need_w >= 0.2 - 1e-9,
  f"+{m.INT_W-need_w:.2f}")
T("емкость >= 200 листов 80 г/м2", int((m.INT_W - A4_W)*10/t80) >= 200,
  f"макс ~{int((m.INT_W-A4_W)*10/t80)}")
T("INT_W = 21.0 + 2.0 + 0.2, PW = INT_W + 1.1",
  abs(m.INT_W - 23.2) < 1e-9 and abs(m.PW - 24.3) < 1e-9)
T("глубина интерьер 30.6 >= A4 29.7", m.INT_H >= A4_H, f"+{m.INT_H-A4_H:.2f}")
T("листы утоплены под кромку входа на 0.9", abs(m.INT_H - A4_H - 0.9) < 1e-9)

# ================= 2. ОДИН КУСОК: раскладка =================
print("--- 2. Один кусок, раскладка ---")
T("высота кроя = 2x31.7 + клапан 6.0 = 69.4",
  abs(m.TOTAL_H - 69.4) < 1e-9 and abs(m.FLAP_BASE - 63.4) < 1e-9)
T("передняя == задняя (31.7 от сгиба)", m.PH == 31.7)
T("крой 24.3 x 69.4 <= целая шкура", m.PW <= 60 and m.TOTAL_H <= 180,
  f"{m.PW} x {m.TOTAL_H}")
xs, ys = [p[0] for p in ol], [p[1] for p in ol]
T("bbox ровно (0,0)..(24.3,69.4)",
  abs(min(xs))<1e-9 and abs(min(ys))<1e-9 and abs(max(xs)-m.PW)<1e-9 and abs(max(ys)-m.TOTAL_H)<1e-9,
  f"x {min(xs):.2f}..{max(xs):.2f}, y {min(ys):.2f}..{max(ys):.2f}")
T("контур замкнут", math.hypot(ol[0][0]-ol[-1][0], ol[0][1]-ol[-1][1]) < 1e-9)
T("симметрия x -> PW-x", max(min(math.hypot(m.PW-p[0]-q[0], p[1]-q[1]) for q in ol)
                             for p in ol) < 1e-6)
T("углы входа ПРЯМЫЕ: (0,0) и (24.3,0) в контуре",
  any(abs(x)<1e-9 and abs(y)<1e-9 for x,y in ol)
  and any(abs(x-m.PW)<1e-9 and abs(y)<1e-9 for x,y in ol))
T("выемка ВНУТРЬ кожи: низ дуги (12.15, +0.6), не торчит за кромку",
  any(abs(x-m.PW/2)<1e-9 and abs(y-0.6)<1e-9 for x,y in ol)
  and min(ys) > -1e-9)
T("проём выемки 2.4: кромки x=10.95/13.35 на y=0",
  any(abs(x-(m.PW/2-1.2))<1e-9 and abs(y)<1e-9 for x,y in ol)
  and any(abs(x-(m.PW/2+1.2))<1e-9 and abs(y)<1e-9 for x,y in ol))
T("углы клапана R15",
  all(any(abs(dist_circle(p[0],p[1],cx,cy,1.5))<1e-9 for p in ol)
      for cx,cy in [(1.5,67.9),(22.8,67.9)]))
T("у сгиба борт сквозной (нет углов): точки (0,31.7) и (24.3,31.7) на бортах",
  any(abs(x)<1e-9 and abs(y-m.PH)<1e-9 for x,y in ol)
  and any(abs(x-m.PW)<1e-9 and abs(y-m.PH)<1e-9 for x,y in ol))

# ================= 3. Шов: 4 сегмента, 2 борта =================
print("--- 3. Шов двух бортов ---")
paths = m.seam_path()
T("ровно 4 сегмента (2 на борт)", len(paths) == 4)
for k, sp in enumerate(paths):
    xs4 = sorted({round(p[0], 6) for p in sp})
    T(f"сегмент {k+1}: вертикаль на борту x=0.4 или 23.9",
      len(xs4) == 1 and min(abs(xs4[0]-0.4), abs(xs4[0]-(m.PW-0.4))) < 1e-6, f"x={xs4[0]}")
    T(f"сегмент {k+1}: отступ 0.4 от входа/сгиба/основы клапана",
      abs(min(p[1] for p in sp) - (0.4 if k % 2 == 0 else m.PH+0.4)) < 1e-9
      and abs(max(p[1] for p in sp) - (m.PH-0.4 if k % 2 == 0 else m.FLAP_BASE-0.4)) < 1e-9,
      f"y {min(p[1] for p in sp)}..{max(p[1] for p in sp)}")
all_holes = []
Lsum = 0.0
for sp in paths:
    holes, total, n = m.punch(sp)
    all_holes += holes; Lsum += total
    gaps = [math.hypot(b[0]-a[0], b[1]-a[1]) for a,b in zip(holes, holes[1:])]
    T(f"сегмент: {n} проколов, шаг 4.5..5.5 мм",
      all(0.45 <= g <= 0.55 for g in gaps), f"{min(gaps)*10:.2f}..{max(gaps)*10:.2f}")
    T("все проколы на полилинии",
      all(min(dist_seg(h[0],h[1], x1,y1,x2,y2)
              for (x1,y1),(x2,y2) in zip(sp, sp[1:])) < 1e-9 for h in holes))
    h2, _, _ = m.punch(sp)
    T("детерминизм", h2 == holes)
T("суммарно 252 прокола", len(all_holes) == 252, f"{len(all_holes)}")
T("вход, сгиб и клапан БЕЗ шва: нет точек с y<0.4, 31.6<y<31.8, y>63.0",
  all(h[1] >= 0.39 and not (31.6 < h[1] < 31.8) and h[1] <= 63.01 for h in all_holes))
# зеркальность наборов: передняя (y 0.4..31.3) vs задняя (31.7..63.0 -> y'=63.4-y)
front = sorted(round(h[1], 6) for h in all_holes if h[1] < m.PH and h[0] < 1.0)
back  = sorted(round(m.FLAP_BASE - h[1], 6) for h in all_holes
               if h[1] > m.PH and h[0] < 1.0)
T("наборы дырок передней и задней совпадают 1:1 при сложении (зеркально)",
  front == back, f"{len(front)} пар")

# ================= 4. Кнопка/ответная =================
print("--- 4. Кнопка ---")
T("кнопка на клапане: y=66.9 = 2.5 от свободной кромки",
  abs(m.BTN_Y - 66.9) < 1e-9, f"y={m.BTN_Y}")
T("ответная на передней: 3.5 над входом", abs(m.MATE_Y - 3.5) < 1e-9, f"y={m.MATE_Y}")
btn_from_fold = abs(m.BTN_Y - m.FLAP_BASE)       # 3.5 над перегибом клапана
T("кнопка и ответная на одном расстоянии от своих перегибов (3.5)",
  abs(btn_from_fold - 3.5) < 1e-9 and abs(m.MATE_Y - 3.5) < 1e-9)
T("при закрытии клапан достаёт до 25.7 от сгиба, листы до 30.2 — накрыты",
  (m.PH - m.FLAP) < (0.52 + A4_H))

# ================= 5. Консенсус и файлы =================
print("--- 5. Файлы и консенсус ---")
s = json.load(open("/root/leather_docs/out_v2/summary.json", encoding="utf-8"))
T("summary.json согласован", s["n_holes"] == 252 and abs(s["path_len"] - round(Lsum,3)) < 1e-9)
try:
    import pymupdf
    d = pymupdf.open("/root/leather_docs/out_v2/lechalo_A2plus_odin_kusok.pdf")
    r = d[0].rect
    T("лист 42x76 см ±1pt", abs(r.width-1190.55)<1.0 and abs(r.height-2154.3)<2.0,
      f"{r.width:.0f}x{r.height:.0f}pt")
    dots = [dr for dr in d[0].get_drawings()
            if dr.get("fill") and dr["rect"].width < 4 and dr["rect"].height < 4]
    T("рендер: 252 шовные точки", len(dots) == 252, f"{len(dots)}")
    txt = d[0].get_text()
    T("тексты: 24.3 / 69.4 / СГИБ / 1:1", all(t in txt for t in ["24.3","69.4","СГИБ","1:1"]))
    d2 = pymupdf.open("/root/leather_docs/out_v2/kontrol_sborki.pdf")
    T("kontrol_sborki.pdf: 1 стр.", len(d2) == 1)
except ImportError:
    T("pymupdf недоступен", True, "SKIP")

print("=" * 62)
print(f"{OK}/{OK+FAIL} passed")
sys.exit(1 if FAIL else 0)