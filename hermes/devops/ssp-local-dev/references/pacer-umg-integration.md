# Стыковка Pacer ↔ SSP ↔ UMG

## Текущее состояние
- SSP `/rtb` отвечает ТОЛЬКО своими direct-кампаниями (сиды mobile/desktop/tv). Обёртки UMG пока нет — до адаптера трафик с Pacer на SSP получает наш тестовый креатив, не UMG.
- Pacer сейчас льёт ~60k attempts/min на UMG напрямую. План: 10k/min → через наш SSP (тестовая кампания), 50k/min — остаётся UMG. 10k/min ≈ 167 rps — gateway тянет с запасом (p95 2.8мс @ 100 rps синтетика).
- Порядок работ: (1) прямой контур Pacer→SSP на direct-кампаниях, (2) UMG demand-адаптер (~3–5 дней), (3) полная цепочка. Не дебажить три звена разом.

## Подключение Pacer к SSP (шаги в UI Pacer)
1. Bid endpoint: name `Lowbid SSP`, URL `https://ssp.lowbid.net/rtb`.
2. Bid request template: обязательно `imp[0].tagid` = ключ зоны (`demo-zone`/`test-zone`), `imp[0].bidfloor` (CPM), `cur: ["RUB"]`; остальное (id, tmax, app/device) Pacer дописывает сам.
3. Apps (бандлы) + Campaign: выбрать endpoint+template, pacing attempts/min, proxy Direct для теста.
4. Контроль: вкладка «Bid attempts» в Pacer (win/no_bid/error, текст ошибки приходит из нашего X-Error); с нашей стороны — логи gateway + ClickHouse; сверка bid.id Pacer↔наши трекинг-URL, допуск по показам ≤15%.

## Гоча
- Гео: кампании таргетированы RU/KZ — не-RU IP устройства (прокси) даст no_bid (fail-closed, 204). Для теста — Direct или RU-прокси.
- Создавать endpoint/кампании в Pacer может только юзер (наш доступ — только код репо); у Pacer есть REST (campaigns, bid_endpoints, bid_request_templates, OAuth cookie /auth) — программно, если юзер даст креды.

## UMG-адаптер (этап A плана partners — в работе)
Архитектура (docs/plan-partners.md): `demand.Source` (интерфейс в app/auction, реализация в infra/umg) → Auctioneer-каскад: партнёрский бид → сборка (цена+наценка, их adm как есть) → fallback на direct-селектор при no-bid/таймауте/ошибке. Существующий direct-путь не менять — каскад ОБОРАЧИВАЕТ его (в rtb.go: auctioneer != nil → каскад, иначе старое поведение). `partner_id` в событиях (0=direct) и CH — добавить ДО первого партнёрского трафика, задним числом не достанешь. Метрики `umg_bid_total{status}`, `umg_bid_seconds`. Включение: запись партнёра в БД (adminctl) + env-флаг; тест с наценкой 0. UMG no-bid = 204, таймаут = min(partner.timeout, остаток tmax), ретраев НЕТ (RTB). Их nurl дёргаем сами при выигрыше (fire-and-forget).
