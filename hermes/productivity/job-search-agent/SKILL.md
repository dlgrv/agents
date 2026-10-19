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
- Roles: Python backend + ML/LLM. Moscow/remote for RU; foreign = remote only, English cover letters (EN-CV at dlgrv.com/cv, RU resume on hh).
- Digest via @fafbbea_bot (token already on hermes-vm; sending with the same token is compatible with the Kuma poller — only getUpdates conflicts, and we never call it).

## Deployment rules

- Everything runs on hermes-vm via `ssh hermes-vm-ts` (direct IP is RF-blocked). Если Tailscale мёртв — рабочая дорога через clash-прокси: `ssh -i ~/.ssh/hermes -o ProxyCommand="nc -X connect -x 127.0.0.1:17890 %h %p" root@178.104.217.93` (см. hermes-vm-stack). Таймзона сервера UTC → таймер на 06:00 UTC (= 09:00 MSK).
- Secrets in `/opt/job-agent/.env` chmod 600 (TELEGRAM_BOT_TOKEN, HH_TOKEN, CHAT_ID, LLM_BASE_URL/API_KEY/MODEL — scorer calls the Hermes LLM provider directly, not local Hermes).
- **hh anonymous search dead:** `/vacancies` отвечает `forbidden` с ЛЮБОГО IP (сервер-датацентр и жилой RU-IP мака, любые UA) — hh закрыли анонимный поиск; справочники (`/dictionaries`, `/areas`) анонимны. Поиск только через авторизованную сессию (hh-applicant-tool или своё OAuth-приложение).
- **Foreign sources verified from server IP:** RemoteOK `/api` OK (ToS требует атрибуцию-ссылку на remoteok.com в дайджесте), WeWorkRemotely RSS OK, HN Algolia OK. Детали: `~/github/job-agent/docs/spike-sources.md`.
- **hh apply IP rule:** the hh API + OAuth token are fine from the server's foreign datacenter IP, but browser automation on hh from it invites captcha/suspicion. If the apply path ends up browser-based, the apply worker lives on the Mac (RU residential IP) and drains a `queued` status from the server DB. LinkedIn/career-ops is the reverse: server-side only, foreign IP reads as natural, and the branch stays off by default (ban risk accepted by user, ≤15 Easy Applies/day).

- **Spike A verdict `api-own`** (детали: `~/github/job-agent/docs/spike-hh-apply.md`, заметки ревью: `~/.hermes/cache/scratch/spike-hh-apply-notes.md`): свой клиент api.hh.ru; из тулзы берём OpenAPI-спеку (`docs/hhapi/openapi.yml` в её репо), OAuth-паттерн (`api/client.py`: креды официального Android-приложения hh, логин телефон/email + разовый SMS-код, `token.json` с авто-refresh ~2 нед, сайт-куки для тестов). Своё OAuth-приложение НЕ регистрируем — один SMS-логин Леонида. Лицензия тулзы разрешает личное использование/модификацию.

## Source adapter quirks (live-verified)

- **RemoteOK `/api`:** первый элемент массива — служебные метаданные (фильтр по наличию `slug`); `salary_min/max = 0` означает «нет данных» → мапить в `None`, иначе дайджест рисует «0–0»; валюты приходят как `USD$`/`EUR€` → CURRENCY_MAP; UA обязателен с контактным email (ToS: атрибуция-ссылка на remoteok.com в дайджесте).
- **HN hiring-треды:** фильтруй по префиксу `ask hn: who is hiring` с начала title — substring-поиск «who is hiring» ловит сторонние посты, упоминающие фразу (ложные треды уходят на скоринг). Через Algolia `search_by_date` они и так попадают в выдачу.
- **LLM-пре-фильтр для иностранки:** foreign-источники прогонять через keyword-пре-фильтр (`sources/prefilter.py`: python/backend/ml/llm/devops/...) ДО скоринга — один прогон без него отдал 100+ нерелевантных вакансий на LLM. hh идёт на полный скоринг без пре-фильтра (русские тайтлы, ключевые слова не покрывают).

## Build workflow (Phase 1+)

- TDD RED-first per task, как в плане; тесты реально ловят баги — чинить код, а не ослаблять тест (капа дня считалась не по apply_log — починено кодом).
- **После фикстурных тестов — живой smoke адаптеров до закрытия майлстоуна:** фикстуры кодируют твои предположения, живые payload'ы их ломают (один прогон вскрыл сразу 3 бага: substring-фильтр HN, нулевые зарплаты RemoteOK, отсутствие пре-фильтра). Формат: один python-скрипт с httpx против живых API + stub-LLM, печатает счётчики и дайджест.
- Держи ruff-конфиг согласованным с кодом: noqa-директивы для выключенных правил (T201, E731) — это RUF100-ошибки; `ruff check --fix` перед коммитом.

## Status

Phase 0 DONE (спайки). **Phase 1 DONE** (44 теста, ruff чист). **Phase 2 core DONE + деплой** (16 коммитов, 59 тестов): hh-клиент (OAuth Android-паттерн, refresh, деликатный delay), LLM-сопроводительные (≤800 симв, без PII, fallback-шаблон), движок откликов (капа 25/день, halt после 2 ошибок подряд, пауза 40с), входная точка `run.py` (--dry-run по умолчанию, --apply явно). **Задеплоено на hermes-vm**: /opt/job-agent, venv python3.14, systemd job-agent.timer 06:00 UTC (09:00 МСК), юниты в repo deploy/. LLM = glmpro (z.ai coding endpoint, glm-5.3-flash, ключ ZAI_API_KEY из /root/.hermes/.env) в /opt/job-agent/.env. **Живой dry-run 2026-10-19: 51 иностранная вакансия заскорена (7 would-apply), дайджест доставлен в Telegram** (@fafbbea_bot, chat 824956847). Скоринг ~51 поз ≈ 8–10 мин последовательно.

Deploy-гочча: rsync обязан исключать `.env` (плюс data/, .venv, .git) — `--delete` без исключения сносил серверные секреты. Юзать `deploy/deploy.sh`. Store-фикс: upsert_new подбирает зависшие в status='new' после прерванного прогона.

Осталось: (1) разовый hh SMS-логин Леонида → scripts/hh_login.md (venv тулзы 2.3.4: ~/.hermes/cache/scratch/hhat-venv), token.json → data/ и на сервер; (2) зарплатная вилка (или «не фильтровать»); (3) неделя dry-run калибровки → переключить ExecStart на --apply; (4) Phase 2.3 чат-респондер (мониторинг negotiations + LLM-ответы, эскалация зарплат/созвонов в Telegram); (5) Phase 3 отклики email на иностранку + LinkedIn-ветка (off по умолчанию).