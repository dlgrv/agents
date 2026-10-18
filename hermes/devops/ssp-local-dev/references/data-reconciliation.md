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

SSP (ssp-deploy → clickhouse-client), сверка — по uniq bid_id:
```sql
SELECT event, count() rows, uniqExact(bid_id) bids FROM ssp.events
WHERE event_time >= now() - INTERVAL 24 HOUR AND buyer_id=1
GROUP BY 1 ORDER BY 2 DESC;
```

Pacer (askpass под dlgrv → host-PostgreSQL lowbid_db):
```sql
SELECT started_at::date, status, count(*) FROM bid_attempts
WHERE campaign_id=<id> AND started_at >= now() - interval '24 hours' GROUP BY 1,2;
-- то же по ad_playback_stats
```

⚠️ Окно ограничено retention: `bid_attempts` держит ~1–7 дней (cron-ретеншн + пересборка), так что сверять можно только свежие сутки, не историю.

## Считать по уникальным бидам, не по строкам
- Строки событий ≠ показы: pacer РЕТРАИТ трекинг-пиксели (`_fetch_tracking_events`), каждый ретрай идёт с новым event_id (новый cachebuster) — дедуп по event_id их пропускает как «разные события». Фактические ориентиры строк за сутки: imp почти без дублей (~1/bid), q75 +16%, complete +4%, q50/start между ними.
- Правильный запрос — `uniqExact(bid_id)` по каждому event: uniq-imp ↔ uniq-complete ↔ pacer `finish` сходятся до ~0.4%. «complete > imp» по строкам — артефакт ретраев, а не рост показов; сверяй uniq-метрики, прежде чем диагностировать.
- Если milestone-дубли загрязняют ЛК, фикс на стороне consumer — дедуп по паре (bid_id, event) для milestone-событий (imp/cv/start/q25/q50/q75/complete/clk: один показ не может дважды дойти до 75%), err остаётся по event_id (разные коды легитимны); метрика ssp_consumer_milestone_dupes_dropped_total.

## Допуски и типовые расхождения
- Допуск ±15% (runbook). Ориентир: uniq imp ↔ uniq complete ↔ pacer finish — доли процента; дельта больше ~1% — искать по методу ниже, а не списывать на «норму».
- Дыра «win → imp» (~25–30% при живом трафике) — НЕ ошибка учёта: плееры байеров не разворачивают Wrapper (таймаут, закрытие приложения), pacer-`error` объясняет лишь треть дыры. Стадийную видимость даёт таблица `ssp.bid_funnel` (req|bid|win|no_bid|qps, минутные агрегаты SummingMergeTree, TTL 30д).

## Процедура
1. Определить окно (свежие ≤24ч из-за retention pacer).
2. Снять CH-срез по buyer_id=1 и pacer-срезы по direct-кампании.
3. Сопоставить uniq-числа по таблице выше, дельты против допуска (сравнение по строкам даст ложную тревогу на milestone-ретраях).
4. Расхождение за допуском → сначала проверить дедуп (двойная вставка event_id = 1 imp) и факт доставки Kafka→CH (рост count()), потом искать потери трафика.
