# Kuma: диагностика «ошибка была, алерт в Telegram не пришёл»

Проверять по порядку — каждая ступень отсекает свою причину. Команды — на хосте через `ssh hermes-vm-ts`; kuma.db = `/opt/uptime-kuma/data/kuma.db` (только read-only SQL: Kuma держит состояние в RAM и откатывает прямые правки при рестарте).

## 1. Монитор вообще привязан к нотификации?
```sql
sqlite3 kuma.db "SELECT monitor_id, notification_id FROM monitor_notification;"
```
Нет строки для монитора → алерты для него не настроены. Мониторы, созданные мимо UI (SQL/API), связок не получают — добавить INSERT в `monitor_notification`.

## 2. DOWN-бит помечен важным?
```sql
sqlite3 kuma.db "SELECT time, status, important FROM heartbeat WHERE monitor_id=<id> ORDER BY time DESC LIMIT 5;"
```
Нотификацию триггерят только биты с `important=1`. `status=0` (down) при `important=0` у push-монитора = `maxretries>0` (первый DOWN считается ретраем) — ставить `maxretries=0`. Если между сбоями cron успевает пушить OK, счётчик ретраев сбрасывается и important никогда не поднимется.

## 3. Kuma пытался отправить и что ответил?
```bash
curl -sm 6 "http://127.0.0.1:3001/api/push/<pushKey>?status=down&msg=triage"
sleep 4
docker logs uptime-kuma --since 2m 2>&1 | grep -A3 "Cannot send"
```
- Тишина → отправка прошла: проблема была в ступенях 1–2.
- `status code 404` → токен маскирован/битый: `sqlite3 kuma.db "SELECT config FROM notification"` — если `"botToken":"<id>:***"` (артефакт миграции v1→v2), заново ввести токен через UI (Settings → Notifications → Test → Save). Реальный токен проверять через Telegram `getMe`; правка БД откатится при рестарте.
- `status code 401/403` → токен отозван/невалиден.
- Нет «Cannot send», но и сообщения нет → сверить `chatID` в конфиге с allowlist поллера.

## 4. После починки
Сбросить тестовый DOWN нормальным пушем (`?status=up&msg=OK`), иначе монитор останется в down.