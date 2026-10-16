# Стыковка Pacer ↔ SSP ↔ UMG

## Текущее состояние
- UMG demand-адаптер (этап A) ВКЛЮЧЁН на проде — см. секцию ниже; `/rtb` работает каскадом: UMG (если жив) → direct-кампании. Осталось: маппинг партнёрского контекста (Partner.TagID + переписывание imp[0].tagid/app при форварде) — без него UMG отвечает 204 даже на реальный трафик Pacer.
- Pacer сейчас льёт ~60k attempts/min на UMG напрямую. План: 10k/min → через наш SSP (тестовая кампания), 50k/min — остаётся UMG.
- Живой каскад с трафиком Pacer: тестовая кампания создана (endpoint → наш /rtb), но UMG отвечает no_bid даже на РЕАЛЬНЫЕ запросы Pacer — их host-ендпоинт сконфигурирован под СВОИ tagid/app-контексты, произвольный tagid даёт 204. Для партнёрских бидов нужен маппинг контекста (Partner.TagID + переписывание imp[0].tagid/app при форварде). 10k/min ≈ 167 rps — gateway тянет с запасом (p95 2.8мс @ 100 rps синтетика).
- Порядок работ: (1) прямой контур Pacer→SSP на direct-кампаниях, (2) UMG demand-адаптер (~3–5 дней), (3) полная цепочка. Не дебажить три звена разом.

## Подключение Pacer к SSP (шаги в UI Pacer)
1. Bid endpoint: name `Lowbid SSP`, URL `https://ssp.lowbid.net/rtb`.
2. Bid request template: обязательно `imp[0].tagid` = ключ зоны (`demo-zone`/`test-zone`), `imp[0].bidfloor` (CPM), `cur: ["RUB"]`; остальное (id, tmax, app/device) Pacer дописывает сам.
3. Apps (бандлы) + Campaign: выбрать endpoint+template, pacing attempts/min, proxy Direct для теста.
4. Контроль: вкладка «Bid attempts» в Pacer (win/no_bid/error, текст ошибки приходит из нашего X-Error); с нашей стороны — логи gateway + ClickHouse; сверка bid.id Pacer↔наши трекинг-URL, допуск по показам ≤15%.

## Гоча
- Гео: кампании таргетированы RU/KZ — не-RU IP устройства (прокси) даст no_bid (fail-closed, 204). Для теста — Direct или RU-прокси.
- Создавать endpoint/кампании в Pacer может только юзер (наш доступ — только код репо); у Pacer есть REST (campaigns, bid_endpoints, bid_request_templates, OAuth cookie /auth) — программно, если юзер даст креды.

## UMG-адаптер (этап A — ВКЛЮЧЁН НА ПРОДЕ)
Архитектура (docs/plan-partners.md): `demand.Source` (интерфейс в app/auction, реализация в infra/umg) → Auctioneer-каскад: партнёрский бид → сборка (цена+наценка, их adm как есть) → fallback на direct-селектор при no-bid/таймауте/ошибке. Существующий direct-путь не менять — каскад ОБОРАЧИВАЕТ его (в rtb.go: auctioneer != nil → каскад, иначе старое поведение). `partner_id` в событиях (0=direct) и CH. Метрики в /metrics: `umg_bid_total{status=bid|no_bid|bad_vast|error}`, `umg_latency_seconds`. Прод-конфиг: UMG_ENABLED=1, `http://r.ussp.io/rtb/3832`, markup 0, timeout 350мс — значения в deploy/.env на сервере, в vps-override только `${VAR:-default}` (литерал перебивает .env). Включение подтверждено логом `umg demand source enabled` + живой тест: синтетика с чужим tagid → честный `no_bid` от UMG → fallback → 204 за ~0.5с (цепочка работает, бид появится от реального трафика Pacer). UMG no-bid = 204, таймаут = min(partner.timeout, остаток tmax), ретраев НЕТ (RTB). Их nurl дёргаем сами при выигрыше (fire-and-forget).

Осталось: маппинг партнёрского контекста для UMG (Partner.TagID, переписывание imp[0].tagid/app при форварде) — без него их host отвечает 204 даже на реальный трафик Pacer.

## Идентификация байеров (план docs/plan-buyer-routing.md)
Решение юзера: `POST /rtb/{id}` — ЧИСЛОВОЙ id (best practice индустрии: ADX/Magnite, тот же UMG `/rtb/3832`), не slug; без legacy-периода — `/rtb` сразу 404 (единственный потребитель мы). Блокеры «bidfloor на external» и «ch-migrate в CD» закрыты (аудит №2); перед вводом остался QPS-limiter per-buyer.

## Диагностика живого каскада (проверенная методика)
Сверять ТРИ источника — по одному они дают противоречивую картину:
1. **Метрики SSP**: `curl 127.0.0.1:18080/metrics | grep umg_` — `umg_bid_total{status}` и `umg_win_total` показывают, что реально прошёл каскад. Работоспособность каскада оценивать только по ним — win'ы в БД Pacer не атрибутированы по endpoint.
2. **Чей VAST в win'ах Pacer**: последний `xml_bodies` из `bid_attempts WHERE status='win'` её БД — маркеры `uSSP`/`<Wrapper` = UMG-ответ, `ssp.lowbid.net`/`/pvast` = наш Wrapper. Отсутствие наших URL в сохранённом теле НЕ доказывает, что наш Wrapper не применялся: плеер может сохранить финальное тело после прохода wrapper-цепочки (их VASTAdTagURI), а не наш первый Wrapper.
3. **Какая кампания родила трафик**: pacer `bid_attempts` не атрибутированы по кампании — win'ы могут идти от прямой UMG-кампании, пока наша тестовая получает 204. Активные кампании+endpoint: `campaigns.bid_endpoint_id` → `bid_endpoints.url`; pacing — `campaign_settings.attempts_per_min`.

Команды (проверены): env — `ssh ssp-deploy` + `set -a; . /home/deployer/krutilka/backend/.env; set +a`; SQL — `docker run --rm --network host -e PGPASSWORD=... postgres:16-alpine psql -h 127.0.0.1 ...`; разбор JSON/XML-полей — скрипт в scratch → `scp` на сервер → `python3` (python-heredoc через вложенные ssh-кавычки молча ломается).

Правило: не подменять верификацию каскада рассуждением о коде — только связка (1)+(2)+(3) различает «каскад не вызывает UMG» / «UMG отвечает no_bid» / «win'ы от другой кампании».

## Эксперимент «проблема не в нас»: reиспользование клиента партнёра
При споре «наш /rtb сломан или UMG не отвечает» — прогнать ЗАПРОС ЧЕРЕЗ КОД КЛИЕНТА ПАРТНЁРА (Pacer BidExecutor, тот же User-Agent и сборка body) против обоих endpoint'ов: наш и прямой UMG. Одинаковые ответы (204 на обоих) = железное доказательство, что SSP прозрачен, и локализует проблему в контексте запроса, а не в нашем коде. Дешевле и убедительнее часового чтения логов.
