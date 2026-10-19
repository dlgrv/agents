---
name: hermes-vm-stack
description: Use when working on hermes-vm, Uptime-Kuma, or @fafbbea_bot.
---

# hermes-vm: сервер и стек мониторинга

## Honcho (self-hosted, :8000)
- **LLM-конфиг двухуровневый: глобальный `LLM_OPENAI_BASE_URL`/`LLM_OPENAI_API_KEY` в .env ПЕРЕКРЫВАЕТСЯ по-компонентным `OVERRIDES__BASE_URL`** (DERIVER_MODEL_CONFIG, DIALECTIC_LEVELS__{minimal..max}, SUMMARY, DREAM_{DEDUCTION,INDUCTION} — всего 10 строк). Симптом неполного переключения: после замены глобального ключа deriver/dialectic ловят 401 `invalid token` от СТАРОГО провайдера (`cometapi_error`), хотя прямой curl с новым ключом проходит. Переключая провайдера, sed'ить все 10 чат-оверрайдов вместе с глобальными ключами.
- Эмбеддинги НЕ переводить на chat-эндпоинт: модель зашита в данных LanceDB — смена эмбеддинг-модели = пере-эмбеддинг всей памяти. Если глобальный ключ меняется, эмбеддингам оставить старый провайдер явным ключом: `EMBEDDING_MODEL_CONFIG__OVERRIDES__API_KEY=<старый ключ>` (строка в .env).
- Проверка связки после правки .env: recreate → `docker logs honcho-local-api-1 | grep PERFORMANCE` (там token counts и total_duration; ноль строк = dialectic ещё не срабатывал) → триггернуть через агентский инструмент `honcho_reasoning`. Логи контейнера эфемерны (теряются при recreate), таблиц usage/token в БД honcho нет — историческое потребление токенов невосстановимо, оценивать по `COUNT(*) FROM messages` × наблюдаемую стоимость вызова.
- AUTH_USE_AUTH=true: клиент обязан слать JWT (Bearer). Плагин берёт ключ из `apiKey` в `~/.hermes/honcho.json` (root или host-блок); без него шлёт заглушку `local` → "Invalid JWT", в логах Hermes это выглядит как `Honcho background session init failed: HTTP 502`.
- Выпуск токена: `ssh hermes-vm-ts 'docker exec -w /app honcho-local-api-1 /app/.venv/bin/python scripts/generate_jwt.py --workspace hermes --print-only'` (в контейнере НЕТ uv — только /app/.venv/bin/python).
- **БАГ образа: `--expires` кладёт exp СТРОКОЙ → PyJWT decode отклоняет ЛЮБОЙ токен с exp.** Токен генерить ТОЛЬКО без --expires (бессрочный; ок для tailnet-only сервиса). Проверка токена: в контейнере `verify_jwt(os.environ['TKN'])`, с мака — SDK `Honcho(workspace_id='hermes', api_key=tok, base_url=...).get_metadata()`.
- Секрет один и тот же в /root/.honcho/profiles/local/{config.toml [auth] JWT_SECRET, .env AUTH_JWT_SECRET} — при рассинхроне подпись не сойдётся.
- Диагностика «все роуты 404»: v1-пути (`/apps`) у v3-сервера отсутствуют валидно; проверять надо SDK-вызовом, не curl по старым путям.

## Сервер
- `hermes-vm` = 178.104.217.93. Таймзона сервера **UTC** (таймеры/кроны считать в UTC: 06:00 UTC = 09:00 MSK).
- Основная дорога — Tailscale: `ssh hermes-vm-ts` (100.93.178.88), алиас настроен на Mac. Прямой SSH по 22-порту: TCP проходит, но баннер не проходит (DPI) — не тратить время на ретраи напрямую.
- Фолбэк, когда Tailscale мёртв — SSH через clash на маке: `ssh -i ~/.ssh/hermes -o ProxyCommand="nc -X connect -x 127.0.0.1:17890 %h %p" root@178.104.217.93` (clash должен быть включён).
- Tailscale может отказывать ОДНОНАПРАВЛЕННО: vm→mac пингуется через DERP, mac→vm — timeout. Прежде чем рестартовать tailscaled, пингануть `tailscale ping` С ОБОИХ концов: если транспорт жив в одну сторону, рестарт серверного демона не помогает — чинить клиент на маке (пересоздание подключения в приложении).
- Старый сервер 193.148.253.171 выведен из эксплуатации (сервисы остановлены) — не использовать.

## Стек на сервере
- Hermes gateway + dashboard (systemd), Telegram-бот @efaecab_bot
- Honcho (Docker Compose, self-hosted) — память о пользователе
- Uptime-Kuma 2.5.4 (Docker, порт 3001, админ root; креды — в kuma-poller.js на сервере, не дублировать)
- SearXNG (Docker, порт 8080 — слушать только tailnet, наружу не открывать; UFW и так прикрывает): метапоиск. Обязательно `format: json` в settings.yml (иначе API отдаёт HTML) и лимитер выключен (запросы только от своих). Порт прибит к tailscale-IP, не к 127.0.0.1 — реальный бинд смотреть `docker port`, а не предполагать localhost. Поиск у обоих агентов идёт через плагин **web-search-plus** (профиль self-hosted): SearXNG — базовый провайдер, keyless Keenable — фолбэк; base_url задаётся в `~/.hermes/plugins/config.json` (`searxng.base_url` = `http://100.93.178.88:8080`), `SEARXNG_URL` в .env провайдером плагина не подхватывается
- **Clash-прокси на маке vs tailnet:** если в `~/.hermes/.env` есть `HTTP_PROXY` (clash), Hermes ходит к 100.93.178.88 ЧЕРЕЗ прокси → Clash не маршрутизирует 100.x → HTTP 502 на каждый запрос (SearXNG «мёртв», honcho init падает). Лечится добавлением `100.93.178.88` в ОБЕ строки `NO_PROXY` и `no_proxy` (нижний регистр обязателен — httpx даёт ему приоритет; `hermes config set` пишет только верхний, нижний — sed'ом). curl при этом работает (игнорирует HTTP_PROXY uppercase) — не обманываться прямой проверкой.
- Работоспособность SearXNG проверять РЕАЛЬНЫМ запросом `curl 'http://100.93.178.88:8080/search?q=test&format=json'` и считать `results`, а не healthz/200 — на IP датацентра апстримы (brave, ddg, qwant, …) блокируют ВСЕ дефолтные движки (rate-limit/CAPTCHA), healthz при этом зелёный, а поиск пустой. Фикс — `/opt/searxng/settings.yml`: включить рабочий движок (bing живой), мёртвые отключить; контейнер монтирует settings.yml — правка на хосте + restart контейнера
- Периодическое обслуживание: диск растёт от логов и контейнеров — `docker system prune` периодически (пользователь одобрил). **Swap 4G добавлен 2026-10-18** (/swapfile, fstab, vm.swappiness=10 — страховка при Ollama ~1.5ГБ). `docker system df` «reclaimable» завышает — `image prune -a` собирает меньше
- Watchtower — автообновления; Kuma на теге `:2` — Watchtower обновляет в пределах минора, мажор не перепрыгнет

## Kuma alert bot (@fafbbea_bot)
Кастомный поллер: у официального Kuma команд в Telegram нет (issue #880 open).
- Код: `/root/.hermes/scripts/kuma-poller.js` (host) → `docker cp` в контейнер `/app/kuma-poller.js`
- Запуск: systemd `kuma-poller.service`; при рестарте убивать старые node-процессы в контейнере (`/tmp/kuma-kill.sh`), иначе Telegram 409 Conflict
- Команды: `/status` (сводка `✅ Up: N 🔻 Down: M`, затем ПУСТАЯ СТРОКА, затем поимённый список всех мониторов; при down — с текстом ошибки), `/start`. Allowlist: chat 824956847. Опрос каждые 3 с.

## Питфоллы Kuma socket.io
- Callback `getMonitorList` возвращает пустой `{}` (и в 1.x, и в 2.x) — реальные мониторы приходят СОБЫТИЕМ `monitorList` после логина; в v2 событие асинхронное и может прийти через ~10 c после login — в пробах ждать ≥25 c, короткое окно даёт ложный «0 мониторов»
- Login-callback в v2 возвращает `{ok, token}` — сам список мониторов в нём НЕ приходит
- Статусы: `getMonitorBeats(id, 1)` → `beats[]`, последний `beat.status` (1=up) — тот же метод, что использует дашборд
- Многострочные node-пробы в контейнер — только файлом: локально → `scp` на хост → `docker cp` в контейнер → `docker exec node file.js`; инлайн-хередоки/кавычки внутри ssh вешают terminal. Рабочий паттерн для многострочных команд по ssh: закодировать в base64 локально и декодировать на хосте — `echo <b64> | base64 -d | timeout N bash`
- Активный поисковый провайдер Hermes не проверять прямым импортом `web_search_registry` в голом python — без загрузки плагинов резолвер возвращает None (ложный негатив). Единственная надёжная проверка — `hermes doctor`
- Пока жив systemd-поллер, НЕ слать ad-hoc `getUpdates` пробы (диагностика «почему бот молчит») — каждый такой вызов конкурирует с поллером и даёт 409 Conflict, маскируя настоящую причину
- Не переносить имена socket-событий между версиями: в v2 обработчики нотификаций переименованы и `getNotifications` не отвечает на callback (вечный TIMEOUT) — конфиг нотификаций читать напрямую из kuma.db (read-only SQL), менять только через UI

## Уведомления (алерты в Telegram)
- Монитор, созданный мимо UI (SQL/скриптом), НЕ получает алерты: связка монитор↔нотификация живёт в таблице `monitor_notification` — вставить строку для каждой пары.
- Push-мониторам, пингуемым чаще раза в минуту (cron), ставить `maxretries=0`: при maxretries>0 первый DOWN помечается retry/PENDING без `important=1` → нотификация не уходит, а следующий OK-пуш сбрасывает счётчик ретраев — алерт не срабатывает никогда.
- Не править конфиг нотификаций через `UPDATE notification SET config=...` в kuma.db: Kuma держит конфиг в RAM и при рестарте откатывает правку назад.
- После мажорного апгрейда проверять токен бота в `notification.config`: миграция v1→v2 маскирует секрет (`"botToken":"<id>:***"`) → Telegram отвечает 404 (URL `/bot<masked>/sendMessage`), при этом `getMe` с реальным токеном проходит. Лечение — через UI: Settings → Notifications → заново ввести токен → Test → Save (одно уведомление обслуживает все мониторы).
- E2E-проверка отправки: `curl "http://127.0.0.1:3001/api/push/<key>?status=down&msg=test"` → через ~4 c `docker logs uptime-kuma --since 1m | grep -iE "telegram|Cannot send"` — тишина = ушло, `Cannot send ... status code NNN` = смотреть код (404 = битый/маскированный токен). Полный порядок диагностики «алерт не пришёл» → references/kuma-alert-triage.md

## Апгрейд Kuma — проверенный порядок (исполнен 1.23.17→2.5.4)
1. Бэкап: `cp -a data data-backup-<date>` в /opt/uptime-kuma (до любых действий)
2. `docker stop && docker rm`, пересоздать на теге `louislam/uptime-kuma:2`
3. Смотреть логи до «Aggregate Table Migration Completed» — миграция НЕОБРАТИМА, не прерывать
4. Файлы, забитые `docker cp` внутрь, ЭФЕМЕРНЫ: пересоздание контейнера (апгрейд, recreate) теряет `/app/kuma-poller.js` и `/tmp/kuma-kill.sh` — после любого пересоздания повторить `docker cp` из `/root/.hermes/scripts/` (источник истины — хост) и `systemctl restart kuma-poller`
5. Проверить: мониторы (8: 6 UI + 2 push Disk/RAM на cron), Telegram-нотификация (токен в конфиге не маскирован, тестовый DOWN-пуш доходит до Telegram), socket-пробой `monitorList`+`getMonitorBeats`
