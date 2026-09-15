---
name: blog-figures-audit
description: Use when drawing SVG diagrams for dlgrv.com blog posts.
---

# Схемы для блога dlgrv.com

Единый рендер: `scripts/build-blog-figures.py` (matplotlib→SVG), запуск через `.venv/bin/python` (uv-venv в репо, matplotlib там). Hand-SVG (pipeline, tokenize) — только Georgia serif, никаких сторонних гарнитур.

## Стандарт
- Все matplotlib-фигуры в ОДНОМ скрипте; rcParams: serif (DejaVu Serif), `svg.fonttype: none`, `savefig.bbox: tight`, pad 0.15 — иначе мёртвые зоны.
- Шкала кеглей: заголовок 16, оси 13.5, аннотации 13, саб-аннотации 12.5 italic #666. Без sans-утечек.
- Ч/б палитра: INK #111, MUTED #666, WARM #555, FAINT #e3e3e3.
- Аннотации НЕ на кривых: размещать в пустом квадранте; подпись на линии — только с белой подложкой (rect) под текстом.
- Подписи-«заголовок схемы» в markdown alt, не в SVG.
- Никакого КАПСа; lowercase везде, кроме аббревиатур (ReLU, T).
- Никаких англицизмов в подписях (проверять 'applied'; 'vs' допустим только в цитате Ына).

## Верификация (обязательна)
1. Отрендерить, скриншот каждой SVG через playwright (файл .cjs — проект ESM!).
2. Прогнать через vision_analyze: «наложения? обрезки? пустые зоны?» — фикс по отчёту.
3. annotate с xycoords='axes fraction' при отрицательном y у соседних панелей СХОДЯТСЯ в центре — наложения между панелями видны только на скриншоте.

## Известные ловушки
- supxlabel не принимает labelpad (Text props) — использовать y=.
- fullPage-скриншот SVG даёт гигантский пустой низ — артефакт скрина, не дефект; смотри viewBox.
- Matplotlib mathtext (10$^{-6}$) и юникод-надстрочные (10⁻⁶) смешивать нельзя — выбрать одно.
