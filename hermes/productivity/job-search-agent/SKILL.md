---
name: job-search-agent
description: Use when working on Leonid's job-agent job-search pipeline.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [automation, job-search, hh]
    related_skills: [hermes-vm-stack, plan]
---

# Job Search Agent (job-agent)

## When to Use

Use when Leonid asks about, continues, or deploys the job-agent pipeline: auto job search (hh.ru, RemoteOK, WeWorkRemotely, HN Who's hiring), LLM scoring against his resume profile, autopilot apply on hh above score threshold, Telegram digest.

Full implementation plan: `~/.hermes/plans/2026-10-19_142240-job-search-agent.md` (phases, task breakdown, file paths). Code repo: локально `~/github/job-agent` (git, приватный; юзер выбрал локальный репо вместо primegit), деплой на hermes-vm в `/opt/job-agent/` (rsync + рестарт юнита; `.venv`/`.env` только на сервере).

## Standing decisions (do not re-litigate)

- **Dry-run week is a hard gate.** Leonid chose full autopilot, but live applies only start after a dry-run week where the digest lists 'would apply on' — he calibrates the threshold. One bad score = a wasted profile view in front of a recruiter.
- Autopilot guards: score ≥ 7/10, cap 25 applies/day (юзер явно поднял с 8/10×10 — «больше откликов»; порог 7 калибруется по dry-run-неделе), stop-words (1C, crypto-scam heuristics), halt + alert after 2 consecutive apply errors.
- Chat auto-reply: юзер хочет, чтобы агент отвечал в чатах hh. Spike A вердикт `api-own`: PyPI-релизы hh-applicant-tool 2.3.5–2.4.4 и main сломаны (SyntaxError `except KeyError, IndexError:`), а `reply-chats --loop` есть только в сломанных 2.4.x → пишем свой responder (GET/POST negotiations по OpenAPI-спеке), логика — референс из кода тулзы.
- Roles: Python backend + ML/LLM. Moscow/remote for RU; foreign = remote only, English cover letters (EN-CV at dlgrv.com/cv, RU resume on hh). Фокус юзера: русскоязычная удалёнка на зарубежные компании — РФ-источники тоже подключаем (он явно разрешил «в рф готов рассмотреть»), но приоритет — зарубежные ру-язычные.
- Digest via @fafbbea_bot (token already on hermes-vm; sending with the same token is compatible with the Kuma poller — only getUpdates conflicts, and we never call it).
- **Дешёвая модель на скоринг/письма:** glm-5.3-flash (`LLM_MODEL` в /opt/job-agent/.env) — юзер отдельно требовал, дорогая glm-5.3 нигде не подключать без явного спроса.
- **Зарплатный фильтр hh:** salary ≥ 250k RUB, ИЛИ зарплата не указана → требуемый опыт ≥ 3 лет (experience прокидывается из парсера).

## Deployment rules

- Everything runs on hermes-vm via `ssh hermes-vm-ts` (direct IP is RF-blocked). Если Tailscale мёртв — рабочая дорога через clash-прокси: `ssh -i ~/.ssh/hermes -o ProxyCommand="nc -X connect -x 127.0.0.1:17890 %h %p" root@178.104.217.93` (см. hermes-vm-stack). Таймзона сервера UTC — все окна таймера пересчитывай в UTC (МСК = UTC+3).
- **Расписание: 3 прогона/день в случайное время** — три 3-часовых окна (МСК 09–12, 14–17, 19–22), случайное смещение внутри окна через systemd `RandomizedDelaySec`; пустой прогон (0 новых вакансий) НЕ пишет в Telegram — только реальный дайджест. `TimeoutStartSec=3600` (масштабируется вместе с охватом).
- **Долгий прогон — только через systemd-юнит + journalctl:** `systemctl start job-agent`, смотреть `journalctl -u job-agent -n N`. Ad-hoc `nohup ... &` через ssh может тихо зависнуть ДО первого вывода (пустой лог, ~0 CPU, полчаса без прогресса) — если запускаешь всё же так: `nohup ... > run.log 2>&1 < /dev/null &` (без `</dev/null` ssh-сессия висит до смерти удалённого процесса), и через минуту отдельной ssh-командой проверяй, что лог растёт, а не только что процесс есть.
- **pgrep -f через ssh самосопоставляется ДАЖЕ с уточнённым паттерном:** удалённый `bash -c` несёт в своей командной строке весь текст паттерна (`pgrep -f "python.*job_agent.run"` матчит сам себя → ложное RUNNING, процесс при этом давно мёртв). Надёжные способы: `systemctl is-active job-agent` для сервисных прогонов; для процессов руками — `ps aux | grep "[j]ob_agent.run"` (скобка ломает само-совпадение) и проверяй, что лог растёт/статусы в БД двигаются, а не только что pid существует.
- Secrets in `/opt/job-agent/.env` chmod 600 (TELEGRAM_BOT_TOKEN, HH_TOKEN, CHAT_ID, LLM_BASE_URL/API_KEY/MODEL — scorer calls the Hermes LLM provider directly, not local Hermes).
- **hh anonymous search dead:** `/vacancies` отвечает `forbidden` с ЛЮБОГО IP (сервер-датацентр и жилой RU-IP мака, любые UA) — hh закрыли анонимный поиск; справочники (`/dictionaries`, `/areas`) анонимны. Поиск только через авторизованную сессию (hh-applicant-tool или своё OAuth-приложение).
- **Foreign sources verified from server IP:** RemoteOK `/api` OK (ToS требует атрибуцию-ссылку на remoteok.com в дайджесте), WeWorkRemotely RSS OK, HN Algolia OK. Детали: `~/github/job-agent/docs/spike-sources.md`.
- **hh apply IP rule:** the hh API + OAuth token are fine from the server's foreign datacenter IP, but browser automation on hh from it invites captcha/suspicion. If the apply path ends up browser-based, the apply worker lives on the Mac (RU residential IP) and drains a `queued` status from the server DB. LinkedIn/career-ops is the reverse: server-side only, foreign IP reads as natural, and the branch stays off by default (ban risk accepted by user, ≤15 Easy Applies/day).

- **Spike A verdict `api-own`** (детали: `~/github/job-agent/docs/spike-hh-apply.md`, заметки ревью: `~/.hermes/cache/scratch/spike-hh-apply-notes.md`): свой клиент api.hh.ru; из тулзы берём OpenAPI-спеку (`docs/hhapi/openapi.yml` в её репо), OAuth-паттерн (`api/client.py`: креды официального Android-приложения hh, логин телефон/email + разовый SMS-код, `token.json` с авто-refresh ~2 нед, сайт-куки для тестов). Своё OAuth-приложение НЕ регистрируем — один SMS-логин Леонида. Лицензия тулзы разрешает личное использование/модификацию.

## Source adapter quirks (live-verified)

- **RemoteOK `/api`:** первый элемент массива — служебные метаданные (фильтр по наличию `slug`); `salary_min/max = 0` означает «нет данных» → мапить в `None`, иначе дайджест рисует «0–0»; валюты приходят как `USD$`/`EUR€` → CURRENCY_MAP; UA обязателен с контактным email (ToS: атрибуция-ссылка на remoteok.com в дайджесте).
- **HN hiring-треды:** фильтруй по префиксу `ask hn: who is hiring` с начала title — substring-поиск «who is hiring» ловит сторонние посты, упоминающие фразу (ложные треды уходят на скоринг). Через Algolia `search_by_date` они и так попадают в выдачу.
- **Лимит hh ~2000 показов/сутки и сортировка:** в каждый hh-поиск шить `"order_by": "publication_time"` — дефолтная сортировка по релевантности отдаёт один и тот же топ на каждом прогоне, и дедуп после первой промывки бэклога оставляет ~0 новых (свежак капает только с новыми публикациями). С `publication_time` хватает per_page=50 (беру СВЕЖИЙ топ каждого запроса; пересечение запросов дедупится). Сейчас 8 поисков × 50 × 3 прогона ≈ 1200 показов/сутки (Python разработчик, Backend Python, ML инженер, LLM, MLOps, Data Engineer — area [1,113]; Python удаленно; ...на английском — без области). Под лимитом держать с запасом — hh-токен общий с авторизацией.
- **Экономия токенов скоринга — рубильники по убыванию эффекта:** (1) качественные пре-фильтры ДО LLM (роли/зарплата/keywords) — самая дешёвая отсечка; (2) cap описания в промпте (сейчас `[:1200]` — стек и требования в начале текста, 1200 хватает для apply/skip); (3) per_page/кол-во запросов hh; (4) дедуп — никогда не скорить дважды. Следующий рычаг при необходимости — батч-скоринг (10 вакансий одним вызовом, −80% вызовов, но грязнее JSON) — юзер cost-ориентирован, предлагать первым, внедрять по явному «давай».
- **Скоринг — параллельный ThreadPoolExecutor (4 воркера):** это самый долгий шаг (LLM-вызов на вакансию). Записи в SQLite (`mark_scored`) — только из главного потока (коннект однопоточный): скори в пуле через `pool.map`, пишите статусы после. Свежие вакансии после расширения: ~250–350 уникальных/день после дедупа.
- **TG-каналы через публичный веб-вью (`GET https://t.me/s/<channel>`):** без ботов и API; обязателен браузерный User-Agent, иначе заглушка. Парсить поточно — искать все вхождения `data-post` и от каждого собирать до следующего: наивный «ближайший div» ломается, потому что между шапкой поста и текстом стоит аватар с закрывающими `</div>`. Финтек-каналы (@fintech_work) дают мало релеванта — держим, но не ждём дайджестного трафика. Похожие источники: Habr Карьера (RSS, ру-язычная удалёнка на зарубежное — главный), remocate.app (список на главной + полные JobPosting в карточках, не JS-рендер). Новый источник всегда: живой curl ДО парсера → TDD-парсер → живой smoke → деплой.
- **LLM-пре-фильтр для иностранки:** foreign-источники прогонять через keyword-пре-фильтр (`sources/prefilter.py`: python/backend/ml/llm/devops/...) ДО скоринга — один прогон без него отдал 100+ нерелевантных вакансий на LLM. hh идёт на полный скоринг без пре-фильтра (русские тайтлы, ключевые слова не покрывают).

## Build workflow (Phase 1+)

- TDD RED-first per task, как в плане; тесты реально ловят баги — чинить код, а не ослаблять тест (капа дня считалась не по apply_log — починено кодом).
- **После фикстурных тестов — живой smoke адаптеров до закрытия майлстоуна:** фикстуры кодируют твои предположения, живые payload'ы их ломают (один прогон вскрыл сразу 3 бага: substring-фильтр HN, нулевые зарплаты RemoteOK, отсутствие пре-фильтра). Формат: один python-скрипт с httpx против живых API + stub-LLM, печатает счётчики и дайджест.
- **Любой LLM-вызов в долгом прогоне: ретраи + изоляция.** Транзиентный 5xx провайдера ретраится (3 попытки, backoff), а неудавшаяся вакансия НЕ должна ронять прогон — лови исключение на пер-вакансию, оставляй её в status='new' (upsert_new/re-pick подберёт на следующем прогоне), считай в errors отчёта. Один 500 убивал весь ран целиком — механизм уже в коде (make_llm_call + _safe_score в pipeline), сохраняй его при рефакторинге.
- Держи ruff-конфиг согласованным с кодом: noqa-директивы для выключенных правил (T201, E731) — это RUF100-ошибки; `ruff check --fix` перед коммитом.

## Status

Phase 0 DONE (спайки). **Phase 1 DONE** (44 теста, ruff чист). **Phase 2 core DONE + деплой** (16 коммитов, 59 тестов): hh-клиент (OAuth Android-паттерн, refresh, деликатный delay), LLM-сопроводительные (≤800 симв, без PII, fallback-шаблон), движок откликов (капа 25/день, halt после 2 ошибок подряд, пауза 40с), входная точка `run.py` (--dry-run по умолчанию, --apply явно). **Задеплоено на hermes-vm**: /opt/job-agent, venv python3.14, systemd job-agent.timer — 3 окна/день (МСК 09–12/14–17/19–22, RandomizedDelaySec), юниты в repo deploy/. LLM = glmpro (z.ai coding endpoint, glm-5.3-flash, ключ ZAI_API_KEY из /root/.hermes/.env) в /opt/job-agent/.env. **Живой dry-run 2026-10-19: 51 иностранная вакансия заскорена (7 would-apply), дайджест доставлен в Telegram** (@fafbbea_bot, chat 824956847). Скоринг ~51 поз ≈ 8–10 мин последовательно.

Deploy-гочча: rsync обязан исключать `.env` (плюс data/, .venv, .git) — `--delete` без исключения сносил серверные секреты. Юзать `deploy/deploy.sh`. Store-фикс: upsert_new подбирает зависшие в status='new' после прерванного прогона.

**Расширение охвата (сделано):** hh SMS-логин Леонида выполнен, token.json на сервере и работает живыми запросами (формат вложенный `{"token": {...}}` — загрузчик читает и плоский, и вложенный, TDD-кейсом); зарплатный фильтр внедрён; 8 hh-поисков × 50 с `order_by=publication_time`; параллельный скоринг (4 воркера); таймер 3×случайное время; экономия токенов (промпт-описание cap 1200, per_page 50). Источников 10: hh, RemoteOK, WWR, HN, Habr Карьера, remocate, TG (@remoteit, @it_remote, @remotejob, @fintech_work). Ретраи/изоляция LLM внедрены после краша прогона на транзиентном 500 z.ai (87 тестов, ruff чист). Живая проверка потока: после первой промывки бэклога следующий прогон с publication_time нашёл 576 показов / 294 новых — стационар ~100–150 новых уникальных/день.

Осталось: (1) неделя dry-run калибровки → переключить ExecStart на --apply; (2) Phase 2.3 чат-респондер (мониторинг negotiations + LLM-ответы, эскалация зарплат/созвонов в Telegram); (3) Phase 3 отклики email на иностранку + LinkedIn-ветка (off по умолчанию).