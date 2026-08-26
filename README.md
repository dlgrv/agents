# ~/.agents — центральный хаб скиллов

Все skills для AI-агентов (Cursor, Codex, Claude Code, Hermes, и др.) живут здесь, в одном месте.
Эта папка — рабочий каталог на диске **и** публичное зеркало: [github.com/dlgrv/agents](https://github.com/dlgrv/agents).

## Добавить skills в проект

```bash
ln -sfn ~/.agents <project>/.agents
```

Симлинк на весь каталог `~/.agents` — в проекте появится всё его содержимое (skills, README и т.д.), и оно всегда актуально.

## Почему симлинк на весь каталог

- **Один источник правды**: обновил что-то в хабе — сразу актуально во всех проектах.
- Cursor надёжно читает `.agents/skills/` только внутри проекта, глобальные пользовательские skills у него работают нестабильно.
- Ноль команд синхронизации, ноль cron'ов, ноль расходящихся копий.

## Структура и происхождение скиллов

Скиллы — **third-party**, взяты с GitHub. Чтобы сохранить атрибуцию и лёгкое обновление,
каждый оригинал лежит как **git submodule** в `_vendor/<repo>/`, а в `skills/` стоит
**symlink** на нужную подпапку внутри него:

```
~/.agents
├── _vendor/                     ← субмодули (кликабельны на GitHub → оригинал)
│   ├── multica-ai__andrej-karpathy-skills/
│   ├── mattpocock__skills/
│   ├── cursor__plugins/
│   ├── shadcn-ui__ui/
│   └── garrytan__gstack/
├── skills/                      ← symlinks → ../_vendor/.../<skill-path>
│   ├── karpathy-guidelines            → multica-ai__andrej-karpathy-skills/skills/karpathy-guidelines
│   ├── improve-codebase-architecture  → mattpocock__skills/skills/engineering/improve-codebase-architecture
│   ├── thermo-nuclear-code-quality-review → cursor__plugins/cursor-team-kit/skills/thermo-nuclear-code-quality-review
│   ├── shadcn                          → shadcn-ui__ui/skills/shadcn
│   └── plan-eng-review                 → garrytan__gstack/plan-eng-review
├── README.md                    ← этот файл
└── LICENSE                      ← MIT (только для моих файлов; субмодули сохраняют свои лицензии)
```

| Skill | Upstream | License (upstream) |
|---|---|---|
| karpathy-guidelines | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | MIT |
| improve-codebase-architecture | [mattpocock/skills](https://github.com/mattpocock/skills) | см. upstream |
| thermo-nuclear-code-quality-review | [cursor/plugins](https://github.com/cursor/plugins) | см. upstream |
| shadcn | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | см. upstream |
| plan-eng-review | [garrytan/gstack](https://github.com/garrytan/gstack) | см. upstream |

## Обновление (pull актуального)

```bash
cd ~/.agents
git pull                                   # superproject (README, .gitmodules, мои файлы)
git submodule update --init --recursive     # после клона на новой машине — подтянуть субмодули
git submodule update --remote --recursive   # обновить third-party до их свежих версий
```

Субмодули «пинируют» конкретный коммит оригинала; «последний» появляется только после `--remote`.

## Как добавить новый third-party skill

1. `git submodule add <url> _vendor/<repo>`
2. `ln -s ../_vendor/<repo>/<skill-path> skills/<name>`
3. `git add skills/<name> _vendor/<repo>` и закоммить.

## Свои материалы

Будущие собственные файлы (промпты, `AGENTS.md`, `CLAUDE.md`, заметки) кладутся как
обычные файлы репо — без субмодулей. Каталог растёт горизонтально, переделок не требует.
