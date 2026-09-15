---
name: primepilot-admin-scaffold
description: Add an admin list table + FastAPI endpoint (primepilot).
---

# Add an admin list page (FastAPI backend + primepilot React admin)

## Trigger
"add a tab to the admin sidebar", "new page in the admin cabin", "show a table of X in admin",
"list endpoint for the admin", "history of X in admin".

## The stack (verify paths in the repo you are in)
- **Backend** `backend/`: FastAPI. `app/managers/*` each subclass `BaseCrudManager` and are wired
  into one `Manager` aggregator (`app/managers/__init__.py`). Routers live in
  `app/api/handlers/*` as `APIRouter(prefix="/api/v1/<x>s")`. Pydantic DTOs in `app/api/entities/*`.
- **Frontend** `frontend/admin/`: React + react-router-dom. Layout/nav in `src/app/App.tsx`
  (`AdminLayout` builds the sidebar from a `nav` array; routes in `src/app/model/routes.ts`).
  Shared UI kit `@primepilot/shared/ui` provides `AppShell`, `PageShell`, `DashboardTableCard`,
  `Table/TableHeader/TableRow/TableCell/TableBody`, `SortableTableHead`, `StatusBadge`,
  `EmptyState`, `PageLoading`, `StatusMessage`. `api()` client lives in `@primepilot/shared/api`.

## Backend — 4 steps
1. **Entity** `backend/app/api/entities/<x>.py`:
   ```python
   from pydantic import BaseModel, ConfigDict
   class <X>Read(BaseModel):
       model_config = ConfigDict(from_attributes=True)
       id: uuid.UUID
       created_at: datetime
       # ...fields mirroring the ORM model
   ```
   Enums (e.g. `OutboundEmailStatus`) can be typed directly — they serialize to `.value`.
2. **Manager** add to `backend/app/managers/<x>.py` (pattern mirrors `registration_application.list_filtered`):
   ```python
   async def list_<x>(self, session, *, limit, offset, sort="created_at", order: SortOrder = "desc"):
       count_stmt = select(func.count()).select_from(Model)
       columns = {"created_at": Model.created_at, "to_email": Model.to_email, ...}  # allowed sort keys
       list_stmt = select(Model).order_by(order_expr(columns[sort], order), Model.id.desc())
       total = int(await session.scalar(count_stmt) or 0)
       rows = list((await session.scalars(list_stmt.limit(limit).offset(offset))).all())
       return rows, total
   ```
   `SortOrder` / `order_expr` are in `app/utils/sorting.py`.
3. **Handler** `backend/app/api/handlers/<x>.py`:
   ```python
   router = APIRouter(prefix="/api/v1/<x>s", tags=["<x>s"])
   @router.get("", response_model=PaginatedResponse[<X>Read])
   async def list_<x>s(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0),
       sort: <X>Sort = Query("created_at"), order: SortOrder = Query("desc"),
       session: AsyncSession = Depends(get_db), manager: Manager = Depends(get_manager),
       _: User = Depends(get_current_admin)) -> PaginatedResponse[<X>Read]:
       items, total = await manager.<x>.list_<x>(session, limit=limit, offset=offset, sort=sort, order=order)
       return PaginatedResponse(items=[<X>Read.model_validate(i) for i in items], total=total, limit=limit, offset=offset)
   ```
   `PaginatedResponse` (`app/api/entities/common.py`: `items, total, limit, offset`) MUST match the
   frontend `ListResponse<T>` field names or the table silently renders nothing.
   Auth: `get_current_admin` (all staff) vs `get_current_owner` + `RequireOwner` guard (owner-only).
4. **Register** in `backend/app/api/handlers/__init__.py`: add `import <x>` and
   `app.include_router(<x>.router)` inside `setup_handlers`.

## Frontend — 3 steps
1. **Routes** `frontend/admin/src/app/model/routes.ts`: add `<x>: "/<x>s"` to `adminRoutes`.
2. **Shell** `frontend/admin/src/app/App.tsx`:
   - `import { <X>Page } from "@/pages/<x>";`
   - push `{ to: adminRoutes.<x>, label: "…", icon: <LucideIcon> }` into the `nav` array in `AdminLayout`
     (after the existing entries; owner-only items use the `...(user?.is_owner ? [...] : [])` spread).
   - add `<Route path={adminRoutes.<x>} element={<XPage />} />` inside the `RequireAuth`→`AdminLayout` block.
3. **Page** `frontend/admin/src/pages/<x>/ui/<X>Page.tsx` + `src/pages/<x>/index.ts` re-export.
   **Copy `pages/organizations/ui/OrganizationsListPage.tsx` as the template** — it already does
   loading / empty / data states, `useColumnSort`, `useIntervalWhenVisible`, and
   `api<ListResponse<T>>('/<x>s?${params}')`. Static (non-sortable) header columns are plain
   `<TableCell>` inside `<TableHeader><TableRow>` — **there is no `TableHead` component** (only `SortableTableHead`).

## StatusBadge for custom statuses
In `frontend/packages/shared/src/shared/ui/StatusBadge.tsx`, add the status to `statusTone`
(`success|danger|warning|pending|neutral|info`) and `statusLabel` (Russian label). Unknown statuses
fall back to neutral + raw value. Extend the shared component rather than passing `label` per-row.

## Verification (commands that actually passed this session)
- Backend wiring: `uv run python -c "from app.api.handlers.<x> import router; print(router.prefix)"`
- Lint: `python -m py_compile <files>` and `uvx ruff@<pinned> check <files>`
- Frontend types: `cd frontend/admin && npx tsc -b`  (per-file `tsc` can't resolve `@/` aliases —
  always use the project `tsc -b`; single-file tsc is skipped by the harness for this reason)
- See `references/architecture.md` for the condensed file inventory.

## Pitfalls
- **`uv.lock` may be virtual-only**: if `pyproject.toml` has no `[project.dependencies]`, `uv sync`
  installs nothing and `main.app` won't boot. Importing the router needs only fastapi/sqlalchemy/pydantic
  — enough to catch wiring bugs. The full app boot needs the whole chain (see references).
- `ListResponse<T>` (frontend) and `PaginatedResponse` (backend) field names must match exactly.
- No `TableHead` component exists — use `TableCell` for static headers.
- The `api()` client auto-prepends `/api/v1`, so page code calls `/<x>s?...` (no prefix).
- Don't add a detail-page click unless asked — the list template wires `rowLinkProps` only when a
  detail route exists; remove it for a list-only page.
