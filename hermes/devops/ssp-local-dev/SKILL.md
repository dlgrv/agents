---
name: ssp-local-dev
description: Use for ortblabs/ssp SSP work — run, deploy, branding.
---

# Lowbid SSP (ortblabs/ssp) — ops и гоча

## Идентификация
- Репо: `ortblabs/ssp` (private), локально `~/aezly/lowbid-ssp`. Проды: https://ssp.lowbid.net (админка + VAST/RTB).
- Коммиты по конвенции `type(ssp-NN): desc` (skill lowbid-git-workflow).

## Деплой (как krutilka)
- CD: GitHub Actions `cd.yaml`, SSH-ключ `ssp_github_actions` → `deployer@135.106.162.15:/home/deployer/ssp` (аналог `deployer_github_actions` у krutilka). Secrets в репо заполнены.
- Цепочка: nginx (ssp.lowbid.net → 127.0.0.1:18080) → gateway-контейнер :8080. `deploy/docker-compose.vps.yaml` лежит В РЕПО (workflow распаковывает fresh-код и снесёт серверный override — не хранить его только на сервере).
- Триггер CD вручную: `gh workflow run cd.yaml --ref main -f branch=main`, статус через ~4.5 мин: `gh run view <run-id> --json status,conclusion`. Живость прода: `curl -X POST https://ssp.lowbid.net/rtb/1 -d '{}'` → 400 (валидация отвечает — сервер жив; голый `/rtb` теперь 404 — buyer-routing закрыл legacy).
- НЕ бандлить push + CD-триггер + sleep в один terminal-вызов: на запрос подтверждения не ответят за таймаут — отменится ВЕСЬ вызов, включая уже выполненные шаги. Сначала спросить юзера, потом push и триггер CD отдельными вызовами.

## КРИТИЧНО: go:embed
Gateway вшивает `frontend/dist` бинарём (`frontend/embed.go`). **Пересобирать gateway СТРОГО после сборки фронта**, иначе на проде/локально отдаётся старый бандл. Проверка: `curl localhost:8080 | grep -o 'assets/index-[^"]*.js'` vs `ls frontend/dist/assets/`.

## Локальный запуск
- Инфра: `docker compose -f deploy/docker-compose.yaml up -d postgres redis redpanda clickhouse` (Docker Desktop).
- Gateway env: `PG_DSN=postgres://ssp:ssp@localhost:5432/ssp?sslmode=disable REDIS_ADDR=localhost:6379 KAFKA_BROKERS=localhost:19092 CH_ADDR=localhost:9000 CH_DB=ssp HTTP_ADDR=:8080 MAXMIND_DB_PATH=~/aezly/krutilka/backend/data/maxmind/.../GeoIP2-City.mmdb` — бинарь в `/tmp/ssp-gateway`.
- **Порт :8080 бывает занят старыми gateway** (в т.ч. `ssp-gw` от subagent-агентов): перед стартом `lsof -i :8080`; pkill-паттерн должен матчить реальное имя бинаря.
- Рейт-лимит логина в Redis: при тестах чистить ключ `login_limit:login:<ip>`.

## Сервер (135.106.162.15)
- SSH: `ssh -i ~/.ssh/id_ed25519_lowbid dlgrv@...`; **одна неудачная попытка = стоп** (fail2ban). sudo через askpass (`SUDO_PASSWORD` в `~/.hermes/.env`, `sshpass -f /tmp/ap.secret sudo -A`).
- ClickHouse: у сервера нет IPv6 — healthcheck только `127.0.0.1` (не localhost → ::1), `listen_host=0.0.0.0`. Миграции/сиды — из контейнера, креды в `deploy/.env` на сервере.
- GeoIP за CF+nginx: реальный IP юзера — **последний** XFF-хоп / `CF-Connecting-IP` (nginx `$proxy_add_x_forwarded_for` ставит CF-IP первым).

## Брендинг (решения юзера)
- Вкладка админки **всегда** «Lowbid SSP» (без динамики по разделам), favicon 📺.
- krutilka на ЕЁ сайте = «Lowbid Pacer», favicon 🌪️; **имена репо не переименовывать**.
- Слово «ortblabs» на сайтах нигде не упоминается.

## Сайдбар / UX
- Тема: тёмная по дефолту (zinc dark), светлая — zinc light; переключатель в подвале сайдбара НАД кнопкой сворачивания, выбор в localStorage, применяется до рендера (анти-мигание скриптом в index.html — страница не вспыхивает тёмным при светлой теме).
- Сайдбар всегда видим (без мобильного Sheet), компакт 3.5rem / расширенный 16rem, состояние в localStorage, кнопка сворачивания внизу сайдбара.
- Гоча: cva-вариант `size default h-8` перебивает базовый `h-10` — кнопки пинить в 40px в обоих состояниях (логотип `size="lg"` 48px тоже ломал геометрию).
- Тесты геометрии: `frontend/sidebar-geometry.test.ts` (unit-инвариант высот) + `frontend/sidebar-geom-check.mjs` (живой замер Y иконок, допуск 1px).
- Масштаб админки: body 17px (крупнее UMG). UX-аудит UMG ВНЕДРЁН ПОЛНОСТЬЮ: H1–H6, M1–M8, L2–L5 (L1 AI-ассистент отложен решением юзера; L2 = таблица «По дням» со sticky-строкой «Всего», агрегат один — `totals(rows)` в lib/stats.ts питает и KPI, и строку). Интеграция с Pacer/UMG: references/pacer-umg-integration.md.

## OpenRTB / стыковка Pacer→SSP→UMG
- Наш /rtb — формально сверен с официальной спекой OpenRTB 2.5 (рус. перевод bidvol.com/docs/oRTB-ru.pdf, 98 стр.) — запушено и задеплоено (CD success). Для разбора PDF-спек: `pypdf` уже стоит — распарсить в scratch-txt и отдавать subagent-ам путь к тексту, а не PDF. Контрактные тесты: 18 (krutilka) + 13 (спека) в `internal/app/rtb/rtb_test.go`: devicetype 1–7, unknown-поля, эхо id, price float CPM, no-bid 204 по §4.2.1.
- Фиксы аудита: request.cur без RUB → 204 (не молча игнорить); в bid-ответе добавлены рекомендуемые `cid` + `adomain` (host ClickURL, опускается если пусто).
- Типы: prebid/openrtb v20.3.0 = OpenRTB 2.6-типы, принимаем 2.5 (обратно совместимо).
- VAST-XML для чужих парсеров: имена тегов сверять СО СПЕКОЙ, не по памяти и не по своим тестам — наш Wrapper писал `<VASTTagUrl>`, спека VAST 3.0 §3.2.3 требует `<VASTAdTagURI>`; чужой парсер (pacer `_required_child_text`) падает AdRequiredChildExtractError, а XML у нас валиден и свои тесты зелёные (тег был захардкожен и в них). При фиксe такого тега грепать тестовое дерево по старому имени — он же в e2e.
- Стыковка Pacer→SSP→UMG: UMG тоже OpenRTB, конвертации не нужно — только dial-in (endpoint+auth) и бизнес-слой (наценка, таймаут-каскад). План 2-кампаний (10к/мин через SSP, 50к/мин напрямую) РЕАЛИЗОВАН и запущен в Pacer; дальше — маппинг партнёрского контекста UMG (см. references/pacer-umg-integration.md).
- Этап A реализован, задеплоен и ВКЛЮЧЁН на проде: домен Partner (миграция 0003), `demand.Source`, каскад в Auctioneer (партнёрский бид с наценкой → no-bid/таймаут → direct), UMG-адаптер (nurl при выигрыше, VAST-Wrapper с нашим трекингом), `partner_id` в событиях, метрики `umg_*` (в /metrics: `umg_bid_total{status}`, `umg_latency_seconds`), adminctl partner-add/list/enable. Прод-конфиг: UMG_ENABLED=1, endpoint r.ussp.io/rtb/3832, markup 0, timeout 350мс (значения в deploy/.env на сервере). Живость каскада подтверждать по периодическому логу `demand cascade reloaded, externals: N` (каждые 30с; `externals: 0` = каскад пуст — env до контейнера не дошёл или партнёров в БД нет) — он надёжнее стартового `umg demand source enabled`, который теряется при рестартах; до реального трафика проверить, что CH-колонка `events.partner_id` применена (см. ниже).
- Диагностика каскада по 204: синтетический запрос с чужим tagid закономерно получит no_bid от UMG (их host ждёт свои хост-контексты) — это НЕ поломка. Цепочка доказана логом `auction external no-bid, partner=umg` + ростом `umg_bid_total{status="no_bid"}`. ВАЖНО: no_bid приходит и на РЕАЛЬНЫЙ трафик Pacer — их host ждёт СВОИ tagid/app-контексты; биды появятся только после маппинга партнёрского контекста (Partner.TagID + переписывание imp[0].tagid/app при форварде). Работоспособность каскада оценивать по метрикам `umg_*`/`umg_win_total`, НЕ по win'ам в БД Pacer (они не атрибутированы по endpoint и могут идти от прямой UMG-кампании). Полная методика диагностики — references/pacer-umg-integration.md.
- CH-миграции НЕ автоприменяются к живым БД (init-скрипты выполняются только на пустом volume). Теперь идемпотентные ALTER прогоняются деплой-скриптом `deploy/ch-migrate.sh` (ADD COLUMN IF NOT EXISTS) — вызывать его из CD до compose up и вручную на любом стенде перед первым трафиком с новой колонкой; проверка факта: `DESCRIBE ssp.events` на ТОМ стенде, где гоняется consumer, а не «на проде когда-то делал». Dev-стенд отстаёт от прода молча — это и есть механизм дрейфа.
- PG-миграции — та же ловушка, с более жёстким отказом: CD выкатывает код раньше, чем миграция применена → gateway crash-loop `relation "partners" does not exist` (запрос к новой таблице на старте). Диагноз: `docker logs ssp-gateway-1` на «relation ... does not exist»; лечение: применить миграцию (docker exec в ssp-postgres-1 или compose-мигрейшн-сервис), затем `up -d` заново. Правило: **каждая новая миграция = шаг в CD-цепочке до compose up**; после CD сверять версию схемы на проде, а не надеяться, что «применял вручную на dev».
- Гоча compose env: `.env` на сервере НЕ действует, если vps-override жёстко прописывает литералы (`UMG_ENABLED: 0` перебивает). В override — только интерполяция `${VAR:-default}` (для UMG это уже в репо — CD-перезапись compose снесёт серверный хак). После `up -d --force-recreate` проверять ФАКТИЧЕСКОЕ окружение контейнера `docker inspect <c> --format '{{range .Config.Env}}{{println .}}{{end}}' | grep VAR` — `docker compose config` может молчать, а контейнер стартовать со старыми значениями.
- Правка файлов на сервере по ssh: python-heredoc через вложенные кавычки молча не применяется (экранирование) — юзать `sed -i` с якорными паттернами (`^      VAR: literal$`) и сразу `grep`-верификацию результата.

## Observability и денежные инварианты (фиксы аудита)
- Новый денежный путь = новые валидации, которых не было у старого: у external-бидов каскада сравнение с `imp.bidfloor` и отсечение price<=0 НЕ наследуются от direct-пути — проверять ЭТИ два места в каждом новом demand-адаптере (пропущенный floor уходит байеру ниже его минимальной цены, нулевая цена выигрывает аукцион).
- Публичные эндпоинты держать консистентными: добавляешь CORS/HEAD на один (для браузерных инспекторов) — сразу на все sibling'и (/vast, /pvast, /vast-tag), иначе следующий инспектор «не работает».
- Метрики: gateway отдаёт `/metrics` на своём :8080 (route до SPA), consumer — ОТДЕЛЬНЫЙ порт (`METRICS_ADDR`, :9090). Сверять target в `deploy/prometheus/prometheus.yml` с фактическим портом — «скрейпит в пустоту» не падает и незаметен без проверки `curl /metrics | grep ssp_`.
- Деньги в CH: агрегаты статистики считать из raw events с дедупом по event_id (argMax) — count() поверх SummingMergeTree-MV задваивает spend при redelivery Kafka (commit-fail после инсерта). Тест: двойная вставка event_id → ровно 1 imp.
- Бюджеты Redis: reserve = один EVAL-скрипт с meta-CAS (смена дневного лимита действует в тот же день, рестарт Redis не сбрасывает потраченное). НЕ lazy-init SetNX полного лимита — это оверспенд.
- Auth: rate-limit логина fail-closed (ошибка Redis → 503); not-found логин сжигает bcrypt на dummy-хэше (анти-тайминг).
- После subagent-раунда с усечённым отчётом (max_iterations) проверять `git status` — хвостовые lint-фиксы остаются некоммиченными; докоммитить и прогнать build/vet/lint самому перед push.

## Фронт-тесты: гоча
- Файл с JSX в тесте называть `.test.tsx`, не `.test.ts` — иначе «Unterminated regular expression literal» (tsx в .ts не парсится).
- В vitest-тестах читать файлы через `process.cwd() + '/src/...'`, не `new URL(..., import.meta.url)` — в jsdom-среде import.meta.url имеет http-схему и readFileSync падает «The URL must be of scheme file».

## Интеграционные тесты: гоча
- Тестируя конкретный SQL-констрейнт (UNIQUE, FK), заполняй ВСЕ поля валидными значениями: zero-value struct (TimeoutMs: 0) упадёт по раннему CHECK-констрейнту вместо целевого UNIQUE — тест проверяет не то, что задуман, и ломается при любом изменении схемы.
- Прогон integration на Mac флейкает через testcontainers/ryuk: перед прогоном чистить мёртвые контейнеры `docker rm -f $(docker ps -aq --filter status=created)`; медленный первый прогон после падения Docker (до ~15 мин).
- Race в тестах таймаутов (tmax запроса == таймауту партнёра): дочерний ctx не должен наследовать родительский дедлайн 1-в-1 — иначе взаимная гонка «кто первый отменит» даёт флейк; тестируй поведение, а не точные тайминги.
- Перед пушем после subagent-раунда: `go test -race ./...` + `go test -tags integration -count=1 ./...` прогонять самому — отчёт агента может быть усечён, а зелёный vitest не покрывает Go-тесты.