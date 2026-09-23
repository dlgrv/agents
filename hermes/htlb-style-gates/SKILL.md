---
name: htlb-style-gates
description: "Use when editing HowToLiveBetter units: capitalize fields."
---

# Стилевые гейты юнитов HowToLiveBetter

- Значение ПОСЛЕ метки поля («- Стоимость:», «- Cost:», «- Costo:» и др., 5 меток на язык) всегда начинается с заглавной буквы. Старые переводы это соблюдали, волны сабагентов нарушали системно (~2600 полей).
- Bulk-fix: regex `^- (?P<lbl>метки): (?P<c>\w)` → upper только первой буквы. Метки: ru — Стоимость|Простыми словами|Эффект|Уровень доказательности|Примечания; en — Cost|In plain terms|Benefit|Evidence grade|Notes; es — Costo|En términos sencillos|Beneficio|Nivel de evidencia|Notas.
- Править одинаково в run-директориях (/root/htlb-run-*/) и собранных book/{ru,en,es}. У вне-волновых глав run-копии бывают stale — book править напрямую безопасно, контент совпадает.
- После bulk-стилевых правок: wave_pipeline (все главы) + check_links, затем коммит. Цитаты/скобки/цифры первым символом не трогаются (\w-фильтр гарантирует).