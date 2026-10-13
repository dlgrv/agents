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

## UMG-адаптер (этап 2, не начат)
Схема: Pacer → наш /rtb → форвард в UMG (их OpenRTB endpoint) → их VAST оборачиваем в наш bid + наценка (revshare) → назад. Пиксели UMG проксируем через наш трекинг (учёт). Fallback: UMG no-bid → наши direct-кампании (селектор уже умеет приоритеты). Критичный риск: латентность UMG должна влезать в наш tmax 550мс — замерить ДО проектирования. Доступ к админке UMG есть (admin.uadex.io) — вытащить формат их bid-endpoint оттуда.
