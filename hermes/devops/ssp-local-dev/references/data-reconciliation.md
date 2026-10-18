# Сверка данных Pacer ↔ SSP (периодическая проверка учёта)

## Семантика статусов pacer (проверено по коду krutilka)
- `bid_attempts.status='win'` = **наш bid-ответ содержал seatbid** (`_extract_bid_status` в bid_executor.py) — «мы ответили бидом», НЕ «показ состоялся». Не путать с выкупом (nurl) и не сравнивать 1:1 с imp.
- `ad_playback_stats.status='finish'` = фактический полный показ у pacer; `error` = ошибка playback.
- Ошибки pacer (`error`) всегда ≥ наших `err`-событий: часть ошибок случается до попадания на наш /err-пиксель.

## Таблица сопоставления (окно сравнения, buyer_id=1 / direct-кампания pacer)

| Стадия | Pacer | SSP (CH) |
|---|---|---|
| Bid-ответы с бидом | `bid_attempts` win | — |
| Показы | `ad_playback_stats` finish | `event='imp'` |
| Полные просмотры | finish | `event='complete'` |
| Ошибки | error | `event='err'` |

## Запросы

SSP (ssp-deploy → clickhouse-client):
```sql
SELECT toDate(event_time), event, count() FROM ssp.events
WHERE event_time >= now() - INTERVAL 24 HOUR AND buyer_id=1
GROUP BY 1,2 ORDER BY 1,2;
```

Pacer (askpass под dlgrv → host-PostgreSQL lowbid_db):
```sql
SELECT started_at::date, status, count(*) FROM bid_attempts
WHERE campaign_id=<id> AND started_at >= now() - interval '24 hours' GROUP BY 1,2;
-- то же по ad_playback_stats
```

⚠️ Окно ограничено retention: `bid_attempts` держит ~1–7 дней (cron-ретеншн + пересборка), так что сверять можно только свежие сутки, не историю.

## Допуски и типовые расхождения
- Допуск ±15% (runbook). Фактические ориентиры: imp ↔ finish сходятся до ~0.1% (дедуп по event_id работает); complete ↔ finish +3% (независимый дедуп пикселей, граница суток) — норма.
- `complete` может превышать `imp` на пару процентов — не баг.
- Дыра «win → imp» (~25–30% при живом трафике) — НЕ ошибка учёта: плееры байеров не разворачивают Wrapper (таймаут, закрытие приложения), pacer-`error` объясняет лишь треть дыры. Стадийную видимость даёт таблица `ssp.bid_funnel` (req|bid|win|no_bid|qps, минутные агрегаты SummingMergeTree, TTL 30д).

## Процедура
1. Определить окно (свежие ≤24ч из-за retention pacer).
2. Снять CH-срез по buyer_id=1 и pacer-срезы по direct-кампании.
3. Сопоставить по таблице выше, дельты против допуска.
4. Расхождение за допуском → сначала проверить дедуп (двойная вставка event_id = 1 imp) и факт доставки Kafka→CH (рост count()), потом искать потери трафика.
