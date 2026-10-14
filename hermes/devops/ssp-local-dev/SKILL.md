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
- Триггер CD вручную: `gh workflow run cd.yaml --ref main -f branch=main`, статус через ~4.5 мин: `gh run view <run-id> --json status,conclusion`. Живость прода: `curl -X POST https://ssp.lowbid.net/rtb -d '{}'` → 400 (валидация отвечает — сервер жив).
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
- Стыковка Pacer→SSP→UMG: UMG тоже OpenRTB, конвертации не нужно — только dial-in (endpoint+auth) и бизнес-слой (наценка, таймаут-каскад). План: в Pacer 2 кампании — 10к/мин через наш SSP (UMG обёрнут), 50к/мин напрямую в UMG.

## Фронт-тесты: гоча
- Файл с JSX в тесте называть `.test.tsx`, не `.test.ts` — иначе «Unterminated regular expression literal» (tsx в .ts не парсится).
- В vitest-тестах читать файлы через `process.cwd() + '/src/...'`, не `new URL(..., import.meta.url)` — в jsdom-среде import.meta.url имеет http-схему и readFileSync падает «The URL must be of scheme file».