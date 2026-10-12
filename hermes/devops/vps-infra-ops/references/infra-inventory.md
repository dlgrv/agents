# Infra inventory & decision log
Updated: 2026-10-12 (plan v3 «Восточный пояс», вариант A — утверждён юзером)

## ACTIVE PLAN: v3 «Восточный пояс» вариант A (2026-10-12)
Контекст: окт.2026 — удары БПЛА по 3 ЦОДам Яндекса (Сасово/Калуга/Владимир);
запад/центр ЕЧР = зона риска, Москва перегружена (миграции с Яндекса).
Решения юзера: VM-only (дедик A и Chipcore E/F выводятся), латентность
+50–70 мс ОК, бюджет ≤60к/мес, критичны PP/GitFlic/GitLab (primebpm — 1 VM
без резерва), LB = 2× HAProxy+keepalived в ru-8 + DNS-DR.
**Раскладка (10 VM, ~56–58к):** Selectel ru-8 NSK — L1,L2,W1,P2,C1 (5);
Selectel Москва, 2 разных ЦОДа — W2 GitLab-standby в ru-2 (Берзарина) +
P1 primebpm в ru-6c (Рябиновая); оба переживают смерть NSK-пула, но не
смерть Selectel целиком; EKACOD Екб — P3 pp-standby + J1 (etcd2+Kuma2);
RUVDS/CloudX Казань — C2 crbsit-standby + etcd3 (судья наложен на standby —
риск «смерть C2 съедает запас судей» принят, как раньше судья на D).
Судью etcd в Москву НЕ ставить: 2/3 судей у Selectel = смерть Selectel
оставляет кворум 1/3 и P3 не сможет стать primary.
etcd-судьи: W1(NSK)+J1(Екб)+C2(Казань) — 3 региона/3 провайдера.
Канонический план + таблица VM + этапы/риски:
`~/.hermes/plans/2026-10-12_104942-east-belt-vm-migration.md`
Каталог провайдеров востока/регионов (55 источников):
`~/.hermes/cache/scratch/hostcat/catalog.md` (мб удалён — факты в плане).
Дедик A: окно расторжения до 05.11.2026 — не пропустить.

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

## Selectel: площадки и пулы (docs.selectel.ru, проверено 12.10.2026)
Москва — 4 своих площадки (зоны доступности): Берзарина 36с3 (ru-2, ru-6b,
ru-7, gis-1, MSK-1/2), Авиамоторная 69 (MSK-3), «Север Москвы» (ru-6a,
адрес скрыт), Рябиновая 53 (ru-6c). **Пул ≠ площадка: ru-2 = ru-7 = одно
здание Берзарина (ФИАС)**; разные ЦОДы в МСК дают только пулы ru-2/ru-7
(Берзарина) vs ru-6a/ru-6c (Север Москвы / Рябиновая). ru-6 — мультизональный
пул по 3 ЦОДам (сегменты a/b/c = разные здания). СПб — 2 группы (Цветочная,
Дубровка), NSK — 1 («Нэкстремум», ru-8). VRRP/keepalived — только внутри
одного пула (нужна общая L2).

## Decision log
- 2026-09-02: NO Cloudflare; DNS = Яндекс. ✔
- 2026-09-02: ONE Selectel account; изоляция файрволом. ✔
- 2026-09-02: NO S3 — взаимные дампы на парный сервер. ✔
- 2026-09-02: Gitflic = 1 VPS, 2 инстанса + 1 общий runner, docker. ✔
- 2026-09-02: Gitflic диск = сетевой HDD 80GB (лёгкая нагрузка). ✔
- 2026-09-02: GitLab-диск 300GB — «там могут быть сборки всякие». ✔
- 2026-09-02: RAM без запаса — «нам запас оперативы и не нужен, это сервер
  для галочки». ✔
- 2026-10-12: География — не держать большинство VM в одном городе; выбран
  вариант A: 5 NSK + 2 Мск (ru-2 + ru-6c, разные ЦОДы) + 2 Екб + 1 Казань. ✔
- 2026-10-12: W2 и P1 разнесены по разным ЦОДам Москвы (Берзарина /
  Рябиновая) — переживают пожар отдельного здания. ✔
- 2026-10-12: Optibit/Красноярск исключён — третий судья etcd наложен на
  C2 (Казань) вместо отдельной VM у мелкого хостера. ✔

## Open questions
- PrimePilot DB: WAL-архив (recommended for license DB) vs hourly dump —
  финальный выбор юзера не зафиксирован.
- Configurator: остаётся на 94.26.228.62 или Object Storage + CDN.
- Точные цены Selectel на момент заказа — сверить в калькуляторе.
