# vimmy — Agent Instructions

Monorepo (Bun workspaces: `apps/*`, `packages/*`). All packages are Cloudflare Workers.

## Commands

Run from the package directory (no root scripts):

| Workspace | Dev | Build | Deploy | Test | Lint | Types |
|-----------|-----|-------|--------|------|------|-------|
| `apps/api` | `bun run dev` (wrangler) | `bun run build` (wrangler dry-run) | `bun run deploy:dev` | — | — | `bun run cf-typegen` |
| `apps/web` | `bun run dev` (vite) | `bun run build` (tsc -b && vite) | `bun run deploy:dev` | — | `bun run lint` (eslint) | `bun run cf-typegen` |
| `packages/shared` | `bun run dev` (wrangler) | — | `bun run deploy` | `bun run test` (vitest) | — | `bun run cf-typegen` |

## Architecture

- **apps/api**: Hono HTTP server, Durable Object (`MyDurableObject`), Drizzle ORM + D1 (SQLite). Entry: `src/index.ts`. Two Drizzle configs: `drizzle.config.ts` (remote D1) and `drizzle.local.config.ts` (local `.db/local.sqlite`). Migrations in `drizzle/`. Deployed as `vimmy-api` on `env.dev`. Bindings (dev env): D1 (`VMMY_DB`), KV (`VMMY_KV`), R2 (`VMMY_BUCKET`), Queue (`VMMY_QUEUE`), DO (`MY_DURABLE_OBJECT`).
- **apps/web**: React SPA via Vite + Cloudflare plugin. Has a separate Cloudflare Worker at `worker/index.ts` (API proxy). Three tsconfigs: `app`, `node`, `worker`. Deployed as `vimmy-web` on `env.dev`.
- **packages/shared**: Zod schemas + JWT (jose). Uses `@cloudflare/vitest-pool-workers`. Tests import from `cloudflare:test`. Entry: `src/index.ts`.

## Conventions

- `worker-configuration.d.ts` is **auto-generated** by `wrangler types` — do not edit manually. Regenerate after changing `wrangler.jsonc` bindings.
- **Formatting**: Prettier (tabs, single quotes, 140 print width). Config per-package, not at root.
- All Workers use `nodejs_compat` compatibility flag.
- `.env` files are gitignored per-workspace. `apps/api/.env` exists locally.

## Stubs / Placeholders

Many files are empty stubs (schemas, routes, services, lib files in `apps/api` and `packages/shared`). Verify a file has content before assuming it implements something.

## CI

`.github/workflows/ci.yml`: runs on PR to `master`. Jobs: `lint-web`, `build-web`, `test-shared`, `typecheck-api`, `build-api`. Uses `oven-sh/setup-bun@v2`.

`.github/workflows/deploy.yml`: runs on push/merge to `master` or `workflow_dispatch`. Applies D1 migrations via `drizzle-kit push`, then deploys both API and Web workers to `env.dev`. Requires secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_D1_TOKEN`.
