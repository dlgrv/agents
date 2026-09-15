# Vitest for an FSD npm-workspaces monorepo

Used in `license-service/frontend` (workspaces: `public`, `cabinet`, `admin`, `packages/shared`, `packages/entities`). Single root config — **no per-package `vitest.config.ts`**.

## Critical: alias ordering

vite's `resolve.alias` matches the **first** entry whose key is a *prefix* of the import specifier. If the base alias `@primepilot/shared` is listed before `@primepilot/shared/api`, an import of `@primepilot/shared/api` is rewritten to `<root>/packages/shared/src/api` (does not exist) → `Failed to resolve import "@primepilot/shared/api"`.

**Fix: every subpath alias MUST come before its base alias.**

```ts
// vitest.config.ts
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      // subpaths FIRST
      "@primepilot/shared/api": fileURLToPath(new URL("./packages/shared/src/shared/api/index.ts", import.meta.url)),
      "@primepilot/shared/ui": fileURLToPath(new URL("./packages/shared/src/shared/ui/index.ts", import.meta.url)),
      "@primepilot/shared/lib": fileURLToPath(new URL("./packages/shared/src/shared/lib/index.ts", import.meta.url)),
      "@primepilot/shared/config": fileURLToPath(new URL("./packages/shared/src/shared/config/index.ts", import.meta.url)),
      "@primepilot/shared/hero-dither": fileURLToPath(new URL("./packages/shared/src/shared/hero-dither/index.ts", import.meta.url)),
      // base AFTER subpaths
      "@primepilot/shared": fileURLToPath(new URL("./packages/shared/src", import.meta.url)),
      "@primepilot/entities/user": fileURLToPath(new URL("./packages/entities/src/entities/user/index.ts", import.meta.url)),
      "@primepilot/entities": fileURLToPath(new URL("./packages/entities/src", import.meta.url)),
      "@": fileURLToPath(new URL("./cabinet/src", import.meta.url)),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    include: ["**/*.test.{ts,tsx}"],
    exclude: ["e2e/**", "node_modules/**", "**/dist/**", "**/playwright-report/**"],
    setupFiles: ["./vitest.setup.ts"],
  },
});
```

**Why file-path aliases (not the package `exports` map):** the workspace uses Node `exports` subpaths (`"@primepilot/shared": { "exports": { "./api": ... } }`). vitest/vite does NOT resolve those subpath `exports` the way Node does, so you must alias every subpath you import to its concrete `index.ts`. List them all.

## Setup file

`vitest.setup.ts` (root):
```ts
import "@testing-library/jest-dom/vitest";
```

## Test location: colocate

Place `*.test.ts(x)` next to the source. FSD: pure functions live in `lib/` and are imported directly by tests. Do **not** export an inner component function just to test it.

## FSD refactor for testability

If a component file contains a pure helper you must test, **extract it to `lib/<name>.ts`** and import it in both the component and the test. Do NOT add `export` to a component-file function — that triggers `react-refresh/only-export-components` lint errors (the file then exports a non-component). Keep component files exporting only the component (plus `forwardRef`/types).

Example from this session: `loginErrorMessage` moved from `LoginPage.tsx` → `cabinet/src/pages/login/lib/loginErrorMessage.ts`; `orgRoleChoices` moved from `OrganizationUsersPanel.tsx` → `packages/entities/.../lib/orgRoleChoices.ts`.

## Dependencies + scripts

`package.json` devDependencies: `vitest`, `jsdom`, `@testing-library/react`, `@testing-library/jest-dom`, `@types/node`.
scripts: `"test:unit": "vitest run"`, `"test:unit:watch": "vitest"`.

## CI separation

Unit tests run in a separate CI job from Playwright **e2e**. e2e needs a running docker stack; unit does not. Add `stage: test` with `npm ci && npm run test:unit` — never run e2e in a pre-commit hook (too slow).

## Verify

After setup: `npx vitest run` → all green. Then run `make frontend` (format + `tsc -b` + `eslint --max-warnings 0` + build) to confirm the new `*.test.ts` files pass lint/typecheck too (eslint's `simple-import-sort` and `react-refresh` apply to test files).

## Playwright E2E isolation (multi-app suite)

Isolate browser state between tests in a public/cabinet/admin suite without leaking auth sessions. **This burned several iterations — capture it.**

### Working pattern

```ts
// helpers/base.ts  (OUTSIDE testDir so Playwright does not collect it as a spec)
import { test as base } from "@playwright/test";

base.beforeEach(async ({ context }) => {
  await context.clearCookies(); // safe on any URL, including about:blank
});

export const test = base;
export { expect } from "@playwright/test";
```

Clear **storage** (localStorage/sessionStorage) only **inside the login helper, AFTER navigating to the app**:

```ts
// e2e/auth.ts
export async function loginWithPassword(page, email, password, totp?, origin?) {
  if (!keepNext) await page.goto(origin ? `${origin}/login` : "/login");
  await page.context().clearCookies();
  await page.evaluate(() => {           // page is now on an http(s) URL → storage IS accessible
    localStorage.clear();
    sessionStorage.clear();
  });
  // ... fill form, submit
}
```

Spec files import `test`/`expect` from `../../helpers/base` (depth depends on folder). `helpers/` sits outside `testDir: "./e2e"`.

### The trap (why the obvious version fails)

`page.evaluate(() => localStorage.clear())` throws
`SecurityError: Failed to read the 'localStorage' property from 'Window': ...`
when the document is **not** an http(s) origin:

- `about:blank` → "Access is denied for this document."
- `data:text/html,...` → "Storage is disabled inside 'data:' URLs."

A `beforeEach` that does `page.goto("data:text/html,<title>x</title>")` to get a navigable page **before** clearing storage fails for exactly this reason and breaks every test in the suite (~50ms each). `context.clearCookies()` is safe because it never touches the page document.

### Pitfalls

- Do NOT put `page.evaluate(storage.clear)` in `beforeEach` unless you first navigate to an http URL inside that same hook.
- Do NOT `page.goto("about:blank")` / `page.goto("data:...")` inside `beforeEach` to "reset" the page.
- Keep shared helpers (`base.ts`, `auth.ts`, `credentials.ts`, `totp.ts`) outside `testDir`; otherwise Playwright collects them as specs and `beforeEach` side effects break collection.
- Per-project `baseURL` (public/cabinet/admin on different ports) belongs in `playwright.config.ts` `projects[].use`, not in the helper.
- When auth uses a unified 401 message (no user-enumeration / no MFA-step leak), the E2E assertion for a wrong-TOTP case must expect the SAME generic text as a wrong-password case — update the test when you unify the message.
- Runtime-error guard used by smoke tests should allowlist controlled 401/404 console errors with an explicit `reason`, so it catches real crashes (pageerror, 5xx) but not expected auth-state 401s from setup/reset flows.
