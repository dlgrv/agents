# Infra inventory & decision log
Updated: 2026-09-02 (plan v2 — evening)

## Current estate
| Host | What runs there |
|---|---|
| 109.236.57.134 (Beget, CRBSIT-BACK) | primebpm.ru (PrimeBPM) + primegit.ru (GitLab CE docker, TLS on host nginx). Дедик 16к/мес; GPU простаивает → демонтаж. |
| 135.106.129.168 | gitflic минфин — уходит, объединяется на одном VPS |
| 217.168.240.89 | gitflic crbsit.ru — уходит, объединяется |
| 94.26.229.45 | PrimePilot: app/admin/api.primepilot.tech; license-service, репо ~/work/license-service (docker compose) |
| 94.26.228.62 | PrimePilot configurator (страница /download); «там ничего не крутится» |

Audit mode: user pastes SSH command output; we do not SSH directly.

## Target architecture (plan v2, 2026-09-02)
- **Web VPS** (Selectel, СПб): 4 vCPU / 8GB / **300GB локальный NVMe** —
  primebpm + primegit (GitLab CE) + host-nginx. ~5–6.5к/мес.
- **Gitflic VPS** (Selectel, Москва): 4 vCPU / 8GB / **80GB сетевой HDD** —
  2 GitFlic инстанса (минфин + crbsit) + **1 общий runner**, всё в docker;
  JVM heap 1–1.5G, runner CONCURRENCY=1, swap 4G. Нагрузка «для галочки»
  (документы, редкий CI). ~3.3–4.3к/мес.
- PrimePilot: отдельные серверы (как сейчас), нулевая связность с main-группой.
- **S3 НЕТ**: бэкапы = взаимные дампы между парными серверами
  (веб ↔ gitflic), prune/retention по cron.
- DNS: **Яндекс DNS**, TTL → 60 за сутки до переезда.
- Failover: GitHub Actions healthcheck (вне нашей инфры) → 3 fails →
  алерт → смена A-записей.
- Итог ~8.5–11к/мес (экономия ~8–13к/мес vs дедик + 2 gitflic-сервера).
- Полный план: ~/.hermes/plans/2026-09-02_165300-infra-failover-selectel.md

## Decision log
- 2026-09-02: NO Cloudflare; DNS = Яндекс. ✔
- 2026-09-02: ONE Selectel account; изоляция файрволом. ✔
- 2026-09-02: NO S3 — взаимные дампы на парный сервер. ✔
- 2026-09-02: Gitflic = 1 VPS, 2 инстанса + 1 общий runner, docker. ✔
- 2026-09-02: Gitflic диск = сетевой HDD 80GB (лёгкая нагрузка). ✔
- 2026-09-02: GitLab-диск 300GB — «там могут быть сборки всякие». ✔
- 2026-09-02: RAM без запаса — «нам запас оперативы и не нужен, это сервер
  для галочки». ✔

## Open questions
- PrimePilot DB: WAL-архив (recommended for license DB) vs hourly dump —
  финальный выбор юзера не зафиксирован.
- Configurator: остаётся на 94.26.228.62 или Object Storage + CDN.
- Точные цены Selectel на момент заказа — сверить в калькуляторе.
