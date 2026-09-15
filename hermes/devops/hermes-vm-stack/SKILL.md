---
name: hermes-vm-stack
description: Use when working on hermes-vm, Uptime-Kuma, or @fafbbea_bot.
---

# hermes-vm: сервер и стек мониторинга

## Сервер
- `hermes-vm` = 178.104.217.93. IP заблокирован в РФ — работать ТОЛЬКО через Tailscale: `ssh hermes-vm-ts` (100.93.178.88), алиас настроен на Mac.
- Старый сервер 193.148.253.171 выведен из эксплуатации (сервисы остановлены) — не использовать.

## Стек на сервере
- Hermes gateway + dashboard (systemd), Telegram-бот @efaecab_bot
- Honcho (Docker Compose, self-hosted) — память о пользователе
- Uptime-Kuma 2.5.4 (Docker, порт 3001, админ root; креды — в kuma-poller.js на сервере, не дублировать)
- SearXNG (Docker, порт 8080 — слушать только tailnet, наружу не открывать; UFW и так прикрывает): метапоиск для `web_search`. Обязательно `format: json` в settings.yml (иначе API отдаёт HTML) и лимитер выключен (запросы только от своих). Используется обоими агентами: `SEARXNG_URL=http://100.93.178.88:8080` в `/root/.hermes/.env` (сервер) и `~/.hermes/.env` (Mac, через tailnet) — интеграция нативная (плагин `plugins/web/searxng`), ключей не нужно. Проверка: `hermes doctor | grep -i search` → `✓ web search (searxng)`
- Периодическое обслуживание: диск растёт от логов и контейнеров — `docker system prune` периодически (пользователь одобрил)
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
