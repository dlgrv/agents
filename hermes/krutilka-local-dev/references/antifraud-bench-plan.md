# Pacer как антифрод-полигон (план по GIVT/SIVT-методологиям)

Спеки: `~/aezly/lowbid-ssp/docs/antifraud/GIVT.md` + `SIVT.md` (взяты извне; MRC/IAB классификация GIVT vs SIVT). Файл с внешнего диска, названный `README.md`, переименовывать по содержимому при переносе в репо — имя README конфликтует с конвенцией репозиториев.

База в krutilka уже есть: `identity/profile_store` (пул профилей ifa/user_id + device-снапшот с UA, квоты), `proxy/soax` (резидентные IP по гео), `event_configs` (jitter/skip на квартили).

## Состояние реализации (обновлять в конце каждой волны)
- Этапы 0–3 (GIVT-персоны: enum, манифест, буфер, alembic, givt:burst bypass квот в Lua) — в коде, задеплоены на прод.
- Этап 4 (SIVT-персоны) — в коде, в main (`feat(lowbid-28)`: fraud_params/night_window + wiring, ту́лтип returning_profiles уточнён), CI зелёный, CD на прод запущен и проверяется. Всё через per-campaign настройки: единый dict `fraud_params` внутри `profile_settings`, принимается API только при `bench_campaign=true` (тот же гейт, что у fraud_mix), дефолты = прод-поведение, вкл/выкл PATCH-ем без деплоя. Ручки: night window (start/end hour, tz_offset), stealth quota_multiplier, whitelist ttl_hours_min/max, burst shows (градации Z), profiles_per_ip до 10 000 (гейт >10 только bench; константа PROD_MAX_PROFILES_PER_IP в user_profile.py). Паттерн `parse_fraud_params(raw, strict)`: strict=True (API-гейт, ValueError) vs strict=False (рантайм, warning + дефолт) — новые ручки добавлять в `services/identity/fraud_params.py`, единственный источник констант.
- Этап 5.1–5.3 — в коде (ждёт коммита `feat(lowbid-30)`; на момент волны проверено: полный suite + flake8/black/ruff/lint-imports зелёные). 5.1 bench stop guards: модуль `backend/app/services/bid/stop_guards.py` (deadline / max_attempts / win_budget), ручки `bench_deadline_seconds`/`bench_max_attempts`/`bench_win_budget` в profile_settings, API-гейт `normalize_bench_guards` в `managers/campaign_settings.py` (тот же паттерн, что у fraud_mix: без `bench_campaign=true` — единый 400). Стоп ОБЯЗАН персиститься через `manager.campaign.mark_stopped`, а не только логироваться — иначе `bid_on_startup` воскресит bench-прогон после рестарта воркера с обнулёнными счётчиками (зомби-паттерн кампании 11). WIN-бюджет: кумулятивный `win_count()` на BidStatBuffer (O(1) в `record()`, переживает флаши) — per-процесс, рестарт воркера обнуляет (задокументированный best-effort; DB-агрегация на горячем пути запрещена). 5.2 realism-fuse: `pool_ips` — поле BidCampaignContext, loader резолвит через инжектируемый `pool_ips_provider` (loader остаётся DB-слоем, scheduler как composition point подставляет `ProxyServiceRegistry.for_pool(id).available_size()`); провайдер упал → None, fuse молчит, никогда не угадывает. 5.3 hot-reload: loop перечитывает контекст раз в `BID_CONTEXT_RELOAD_INTERVAL_SECONDS` (env, дефолт 45с, dataclass `BidScheduler` в settings.py); swap атомарный по ссылке (in-flight попытки доигрывают свою генерацию), `is_running=false` → graceful stop, semaphore осознанно НЕ пересоздаётся (фиксированный cap, темп правит token bucket).
- Остаток этапа 5: 5.4 arq TTL 900с для bench-executor (`_expires`); 5.5 изоляция bench-подпула от прод-пула; 5.6 `scripts/bench_preflight.py` (баланс soax, Redis noeviction, test-WIN до ssp.events, freeze-проверка); 5.7 вотчер кредитов с жёстким стопом. Далее: 6 (reporting), 7 (первый bench-ран; перед ним квоты bench-кампаниям по формуле lease-бюджета).
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
