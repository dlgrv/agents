# Стыковка Pacer ↔ SSP ↔ UMG

## Текущее состояние
- Цепочка Pacer → SSP → UMG ЖИВАЯ на проде: `umg_bid_total{status="bid"}`, `umg_win_total` растут, external win идут, `/pvast` дергается плеерами (23/5мин после фикса тега), `/nurl` нотисы идут. Прорыв дал маппинг контекста: pacer шлёт `tagid: smarttv_preroll_main` — под него создана зона в SSP, после этого UMG начал бидовать на реальном трафике.
- Buyer-routing реализован: `POST /rtb/{id}` (числовой, Pacer = id 1), голый `/rtb` → 404, домен Buyer + миграция 0005 + кэш, QPS-limiter per-buyer (fail-open, лимит в админке). Ранний `AdRequiredChildExtractError` в pacer (playback после win) — был наш Wrapper с тегом `<VASTTagUrl>` вместо спекового `<VASTAdTagURI>`; фикс в wrapper.go + e2e-тесте. Следом тот же класс: в Wrapper-Linear был только creativeView → start/q25/q50/q75/complete = 0 при живом playback (прогресс уходил в inner-InLine партнёра); добавлена полная воронка wrapper-level — pacer мержит и дёргает оба набора. **clk=0 от Pacer — НОРМА**: их playback-флоу не эмулирует клики (VideoClicks парсится, но не срабатывает); клики ждать только от живых плееров прямых кампаний.
- Раздел «Байеры» в ЛК SSP: CRUD + live-счётчики из CH + копирование endpoint. UMG-каскад (этап A) включён на проде — секция ниже.
- Порядок работ: (1) прямой контур Pacer→SSP на direct-кампаниях, (2) UMG demand-адаптер (~3–5 дней), (3) полная цепочка. Не дебажить три звена разом.

## Подключение Pacer к SSP (шаги в UI Pacer)
1. Bid endpoint: name `Lowbid SSP`, URL `https://ssp.lowbid.net/rtb/1` (числовой buyer-id; голый `/rtb` закрыт 404).
2. Bid request template: обязательно `imp[0].tagid` = ключ зоны (`demo-zone`/`test-zone`), `imp[0].bidfloor` (CPM), `cur: ["RUB"]`; остальное (id, tmax, app/device) Pacer дописывает сам.
3. Apps (бандлы) + Campaign: выбрать endpoint+template, pacing attempts/min, proxy Direct для теста.
4. Контроль: вкладка «Bid attempts» в Pacer (win/no_bid/error, текст ошибки приходит из нашего X-Error); с нашей стороны — логи gateway + ClickHouse; сверка bid.id Pacer↔наши трекинг-URL, допуск по показам ≤15%.

## Гоча
- Гео: кампании таргетированы RU/KZ — не-RU IP устройства (прокси) даст no_bid (fail-closed, 204). Для теста — Direct или RU-прокси.
- Создавать endpoint/кампании в Pacer может только юзер (наш доступ — только код репо); у Pacer есть REST (campaigns, bid_endpoints, bid_request_templates, OAuth cookie /auth) — программно, если юзер даст креды.

## UMG-адаптер (этап A — ВКЛЮЧЁН НА ПРОДЕ)
Архитектура (docs/plan-partners.md): `demand.Source` (интерфейс в app/auction, реализация в infra/umg) → Auctioneer-каскад: партнёрский бид → сборка (цена+наценка, их adm как есть) → fallback на direct-селектор при no-bid/таймауте/ошибке. Существующий direct-путь не менять — каскад ОБОРАЧИВАЕТ его (в rtb.go: auctioneer != nil → каскад, иначе старое поведение). `partner_id` в событиях (0=direct) и CH. Метрики в /metrics: `umg_bid_total{status=bid|no_bid|bad_vast|error}`, `umg_latency_seconds`. Прод-конфиг: UMG_ENABLED=1, `http://r.ussp.io/rtb/3832`, markup 0, timeout 350мс — значения в deploy/.env на сервере, в vps-override только `${VAR:-default}` (литерал перебивает .env). Включение подтверждено логом `umg demand source enabled` + живой тест: синтетика с чужим tagid → честный `no_bid` от UMG → fallback → 204 за ~0.5с (цепочка работает, бид появится от реального трафика Pacer). UMG no-bid = 204, таймаут = min(partner.timeout, остаток tmax), ретраев НЕТ (RTB). Их nurl дёргаем сами при выигрыше (fire-and-forget).

Маппинг контекста РЕАЛИЗОВАН (зона под tagid pacer'а) — именно после него UMG начал бидовать на реальном трафике; их host отвечает 204 на произвольные tagid, зона должна существовать в SSP.

## Идентификация байеров (план docs/plan-buyer-routing.md)
Решение юзера: `POST /rtb/{id}` — ЧИСЛОВОЙ id (best practice индустрии: ADX/Magnite, тот же UMG `/rtb/3832`), не slug; без legacy-периода — `/rtb` сразу 404 (единственный потребитель мы). РЕАЛИЗОВАНО и на проде: домен Buyer (миграция 0005) + кэш, QPS-limiter per-buyer fail-open (429 при превышении — растить лимит байера в админке, не дебажить как баг; QPS = ЗА СЕКУНДУ, rpm байера делить на 60: 3000 rpm ≈ 50 QPS, а дефолт нового байера легко ниже pacing кампании — массовые 429 «со всеми ошибками» это лимит, не поломка), buyer_id пишется во все события.

## Диагностика живого каскада (проверенная методика)
Сверять ТРИ источника — по одному они дают противоречивую картину:
1. **Метрики SSP**: `curl 127.0.0.1:18080/metrics | grep umg_` — `umg_bid_total{status}` и `umg_win_total` показывают, что реально прошёл каскад. Работоспособность каскада оценивать только по ним — win'ы в БД Pacer не атрибутированы по endpoint. Метрики контейнера СБРАСЫВАЮТСЯ рестартом (деплой) — «маленькие числа» после деплоя это новый отсчёт, не деградация.
2. **Чей VAST в win'ах Pacer**: последний `xml_bodies` из `bid_attempts WHERE status='win'` её БД — маркеры `uSSP`/`<Wrapper` = UMG-ответ, `ssp.lowbid.net`/`/pvast` = наш Wrapper. Отсутствие наших URL в сохранённом теле НЕ доказывает, что наш Wrapper не применялся: плеер может сохранить финальное тело после прохода wrapper-цепочки (их VASTAdTagURI), а не наш первый Wrapper.
3. **Какая кампания родила трафик**: pacer `bid_attempts` не атрибутированы по кампании — win'ы могут идти от прямой UMG-кампании, пока наша тестовая получает 204. Активные кампании+endpoint: `campaigns.bid_endpoint_id` → `bid_endpoints.url`; pacing — `campaign_settings.attempts_per_min`.

Захват реального запроса pacer — самый короткий путь при «каскад не бидует»: логировать/дампить один живой body с `/rtb/1` (tagid, bidfloor+cur, bundle, geo) и сверять с нашими зонами/таргетами — синтетика с придуманными полями проверяет не тот путь. Не подменять верификацию каскада рассуждением о коде — только связка (1)+(2)+(3) различает «каскад не вызывает UMG» / «UMG отвечает no_bid» / «win'ы от другой кампании».

«Статус 200 при нулевых бидах» = 200-путь с пустым seatbid (домен-заглушка): считать биды по `umg_bid_total`/adm в ответах, не по HTTP-статусам.

Команды (проверены): env — `ssh ssp-deploy` + `set -a; . /home/deployer/krutilka/backend/.env; set +a`; SQL — `docker run --rm --network host -e PGPASSWORD=... postgres:16-alpine psql -h 127.0.0.1 ...`; разбор JSON/XML-полей — скрипт в scratch → `scp` на сервер → `python3` (python-heredoc через вложенные ssh-кавычки молча ломается).

Правило: не подменять верификацию каскада рассуждением о коде — только связка (1)+(2)+(3) различает «каскад не вызывает UMG» / «UMG отвечает no_bid» / «win'ы от другой кампании».

## OpenRTB-контракт и валидация артефактов наружу
- Наш /rtb формально сверен с официальной спекой OpenRTB 2.5 (рус. перевод bidvol.com/docs/oRTB-ru.pdf, 98 стр.). Для разбора PDF-спек: `pypdf` уже стоит — распарсить в scratch-txt и отдавать subagent-ам путь к тексту, а не PDF. Контрактные тесты: 18 (krutilka) + 13 (спека) в `internal/app/rtb/rtb_test.go`: devicetype 1–7, unknown-поля, эхо id, price float CPM, no-bid 204 по §4.2.1. Аудит-фиксы: request.cur без RUB → 204 (не молча игнорить); в bid-ответе рекомендуемые `cid` + `adomain` (host ClickURL, опускается если пусто). Типы: prebid/openrtb v20.3.0 = OpenRTB 2.6-типы, принимаем 2.5 (обратно совместимо).
- VAST-XML для чужих парсеров: имена тегов сверять СО СПЕКОЙ, не по памяти и не по своим тестам — наш Wrapper писал `<VASTTagUrl>`, спека VAST 3.0 §3.2.3 требует `<VASTAdTagURI>`; чужой парсер падает AdRequiredChildExtractError, а XML валиден и свои тесты зелёные (тег был захардкожен и в них). При фиксе такого тега грепать тестовое дерево по старому имени — он же в e2e. Матчить префиксом (`<Wrapper`, не `<Wrapper>`): тег с атрибутами (`allowMultipleAds`) точной строкой не матчится — ассерт слепо пропускает реальный Wrapper. Wrapper-level Tracking — ПОЛНАЯ воронка (start/q25/q50/q75/complete), не только creativeView: плееры байеров мержат wrapper-трекинг с inner-InLine; неполный набор = прогресс external-показов уходит партнёру, у нас нули при живом playback (тест — assert на ВСЕ события воронки). Валидировать генерируемый XML ТОЛЬКО внешним эталоном: официальный IAB VAST 3.0 XSD вендорен в `internal/app/vast/testdata/xsd/vast3.xsd`, тесты гоняют `xmllint --noout --schema` (без xmllint — SKIP с подсказкой; CI ставит `libxml2-utils`). Golden, сгенерированный нашим же билдером, ничего не доказывает — он ловит только регрессию против себя; XSD с первого прогона поймала порядок элементов (Error ДО Impression, §2.3.2.1) и оба исторических бага имён. Общее правило для ЛЮБОГО артефакта наружу (VAST, CSV, JSON админки, Kafka-события) — docs/CODE-STANDARD.md §7 в репо.

## Эксперимент «проблема не в нас»: reиспользование клиента партнёра
При споре «наш /rtb сломан или UMG не отвечает» — прогнать ЗАПРОС ЧЕРЕЗ КОД КЛИЕНТА ПАРТНЁРА (Pacer BidExecutor, тот же User-Agent и сборка body) против обоих endpoint'ов: наш и прямой UMG. Одинаковые ответы (204 на обоих) = железное доказательство, что SSP прозрачен, и локализует проблему в контексте запроса, а не в нашем коде. Дешевле и убедительнее часового чтения логов.
