# Condensed architecture map (license-service / primepilot-style)

Verified during the "История писем" (OutboundEmail) admin feature. Paths relative to repo root.

## Backend (`backend/`)
- App entry: `main.py` → `app = FastAPI(...)`, then `setup_handlers(app)` (in `app/api/handlers/__init__.py`).
- Routers: `app/api/handlers/<x>.py`, each `APIRouter(prefix="/api/v1/<x>s", tags=["<x>s"])`,
  registered in `setup_handlers` via `app.include_router(<x>.router)`.
- DTOs: `app/api/entities/<x>.py`. Common: `PaginatedResponse[T]` in `app/api/entities/common.py`
  fields = `{items, total, limit, offset}`.
- Managers: `app/managers/<x>.py` subclass `BaseCrudManager[Model]`; all wired into the `Manager`
  aggregator in `app/managers/__init__.py` (e.g. `self.mail = MailManager(model=OutboundEmail)`).
  List pattern to copy: `registration_application.list_filtered` (count + select, `order_expr` from
  `app/utils/sorting.py`, tiebreak on `id.desc()`).
- Deps: `app/api/deps.py` → `get_db`, `get_manager`, `get_current_admin`, `get_current_owner`.
- ORM: `app/database/models.py`. `Base` adds `id` (UUID), `created_at`, `updated_at`.
- Enums (StrEnum): `app/utils/enums.py` — e.g. `OutboundEmailKind`, `OutboundEmailStatus`
  (sent/failed/skipped).
- `OutboundEmail` table: kind, to_email, subject, body_preview, status, error (nullable).

## Frontend (`frontend/admin/`)
- Routing + sidebar: `src/app/App.tsx` → `AdminLayout` builds `nav` array (label + icon + optional
  `badge`; owner-only items via `...(user?.is_owner ? [...] : [])`), `requireAuth` guard.
  Routes in `src/app/model/routes.ts` (`adminRoutes` const).
- Page template to copy: `src/pages/organizations/ui/OrganizationsListPage.tsx`
  (loading/empty/data states, `useColumnSort`, `useIntervalWhenVisible`, `api<ListResponse<T>>`).
- Shared UI: `@primepilot/shared/ui` — `AppShell, PageShell, DashboardTableCard, Table*
  (Table, TableHeader, TableRow, TableCell, TableBody), SortableTableHead, StatusBadge, EmptyState,
  PageLoading, StatusMessage`. NOTE: no `TableHead` component — static headers use `<TableCell>`.
- `api()` client (`@primepilot/shared/api`) auto-prepends `/api/v1`; page code calls `/<x>s?...`.
- `StatusBadge` (`frontend/packages/shared/src/shared/ui/StatusBadge.tsx`): extend `statusTone`
  (success/danger/warning/pending/neutral/info) and `statusLabel` (Russian) for new statuses.

## Verification commands that passed
- `uv run python -c "from app.api.handlers.<x> import router; print(router.prefix)"` → `/api/v1/<x>s`
- `python -m py_compile <files>` and `uvx ruff@0.11.7 check <files>`
- `cd frontend/admin && npx tsc -b` (clean)

## Environment caveat (NOT a durable rule — was a transient setup state)
At the time of this feature, `backend/pyproject.toml` had no `[project.dependencies]` and `uv.lock`
was virtual-only, so `uv sync` installed nothing. Router import worked after `uv pip install`-ing the
chain: fastapi, sqlalchemy[asyncio], pydantic, aiosmtplib, redis, python-dotenv, asyncpg, argon2-cffi,
pyotp, qrcode, httpx, pydantic-settings, email-validator, fakeredis. Full `main.app` boot needs all of
these; importing a single handler/router needs only fastapi+sqlalchemy+pydantic. Re-check whether the
repo now declares deps before assuming `uv sync` is broken.
