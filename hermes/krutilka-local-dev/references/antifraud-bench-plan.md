# Pacer как антифрод-полигон (план по GIVT/SIVT-методологиям)

Спеки: `~/aezly/lowbid-ssp/docs/antifraud/GIVT.md` + `SIVT.md` (взяты извне; MRC/IAB классификация GIVT vs SIVT). Файл с внешнего диска, названный `README.md`, переименовывать по содержимому при переносе в репо — имя README конфликтует с конвенцией репозиториев.

База в krutilka уже есть: `identity/profile_store` (пул профилей ifa/user_id + device-снапшот с UA, квоты), `proxy/soax` (резидентные IP по гео), `event_configs` (jitter/skip на квартили).

## Состояние реализации (обновлять в конце каждой волны)
- Этапы 0–3 (GIVT-персоны: enum, манифест, буфер, alembic, givt:burst bypass квот в Lua) — в коде, задеплоены на прод.
- Этап 4 (SIVT-персоны) — в коде, ревью пройдено; деплой ждёт явного «да». Всё через per-campaign настройки: единый dict `fraud_params` внутри `profile_settings`, принимается API только при `bench_campaign=true` (тот же гейт, что у fraud_mix), дефолты = прод-поведение, вкл/выкл PATCH-ем без деплоя. Ручки: night window (start/end hour, tz_offset), stealth quota_multiplier, whitelist ttl_hours_min/max, burst shows (градации Z), profiles_per_ip до 10 000 (гейт >10 только bench; константа PROD_MAX_PROFILES_PER_IP в user_profile.py). Паттерн `parse_fraud_params(raw, strict)`: strict=True (API-гейт, ValueError) vs strict=False (рантайм, warning + дефолт) — новые ручки добавлять в `services/identity/fraud_params.py`, единственный источник констант.
- Далее по плану: этап 5 (bench-guard), 6 (reporting), 7 (первый bench-ран; перед ним квоты bench-кампаниям по формуле lease-бюджета).
- Ночной гейт стоит ПОСЛЕ lease-acquire и до bid-запроса (sticky-персона на reuse главнее драу), исход показа вне окна — честный ERROR `NightWindowClosedError`, квотный счётчик при этом тратится (сигнал ночи живёт в манифесте, не в счётчиках). Churn TTL=0 реализован как «lease истёк + grace 60 c» (`COOKIE_CHURN_GRACE_SECONDS`): Redis EXPIRE 0 удалил бы профиль до чтения после acquire.

## Персоны поверх identity-профиля (поле `persona` в профиле)

| Персона | Искажение | Проверяет |
|---|---|---|
| `clean` | как сейчас: soax-прокси, живой UA, человеческие тайминги, стабильный ifa | контроль false positives (должна НЕ детектиться) |
| `givt:dc_ip` | запрос без прокси — серверный IP сам по себе дата-центровый | GIVT №1 (дата-центры) |
| `givt:bad_ua` | UA `python-requests`/`curl`/пустой при живом IP | GIVT №2 |
| `givt:declared_bot` | UA `SomethingBot/1.0 (+crawler)` | GIVT №3 |
| `givt:burst` | 5–10 показов с одного ifa за 2–3 сек, дубли тэгов | GIVT №4/№5 |
| `givt:instant_close` | `skip_chance=100` после start, dwell ≈ 0 | GIVT №4 (сессия) |
| `sivt:night` | окно активности 01:00–05:00 (сдвиг расписания воркера) | фича «ночная активность» |
| `sivt:device_farm` | много уникальных ifa с одного IP, одинаковый UA | концентрация устройств, Джини |
| `sivt:cookie_churn` | новый ifa на каждый показ → cookie_age=0 | cookie lifetime |
| `sivt:stealth` | резидентный IP + живой UA + нормальные тайминги, но аномальный объём с одного IP | то, что GIVT обязан пропустить, а SIVT поймать по Z-score — разделяет уровни |

## Ground truth — сердце стенда
Pacer единственный знает, какие показы фейковые. Каждому playback-пакету — session_id + persona; воркер пишет манифест `ts, ifa, ip, zone, persona, campaign` (PG или отдельный endpoint). Скрипт джойнит манифест с вердиктами антифрода SSP (по ifa+ip+ts) → precision/recall/FPR по каждой персоне.

## Бенчмарк-режим
CLI/API: «крути N часов, смесь 80% clean / 10% givt / 10% sivt» + отчёт ожидаемых долей. Контрольные цифры — из SIVT.md (CRITICAL 1–3%, NO_FRAUD 40–60%; >5% CRITICAL = алерт).

## Ограничения
- soax sticky-сессия держит exit IP только под непрерывным трафиком (интервалы ~10 с — IP стабилен; простой >60 c — ротация). Многочасовые «стабильные IP-персоны» невозможны: стабильный идентификатор персоны — ifa из profile store, ip в манифесте пишется как наблюдаемый, джойн манифест↔вердикты — по ifa+ts, не по постоянству IP.
- Клики не возвращать (директива байера, симуляторные клики вырезаны из прода) — из референсных 42 фичей CTR-аномалии выпадают, это ок для видео.
- Бurst/дата-центровые персоны сжигают бюджет: бенчмарк крутить только на direct-кампании с малым бюджетом, не на прод-каскаде UMG.
- Порядок: GIVT-персоны + манифест первыми (мало кода — GIVT-фильтр в SSP можно писать сразу с валидацией), SIVT-персоны — когда дойдёт до скоринга.
