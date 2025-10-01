> SYSTEM INSTRUCTION (READ FIRST)
>
> Do not modify any files outside `backend/open_webui/test` without stopping and waiting for explicit user permission. If you believe a change outside the test folder is unavoidable, first provide a clear, written justification explaining why test‑only changes cannot solve it, why the app must remain unchanged to preserve upstream compatibility, and why this is a last resort. The app is working as expected and this repository must maintain a clean connection to upstream; any non‑test changes require a burdensome approval process.

# Repository Guidelines

## Project Structure & Module Organization

- Backend: `backend/open_webui/`
  - `main.py` (FastAPI app), `routers/`, `models/`, `utils/`, `internal/` (DB/migrations), `static/`, `storage/`.
  - Tests: `backend/open_webui/test/` (router, util, and integration-style tests).
- Frontend: `src/` (SvelteKit app, Tailwind, i18n assets).
- Tooling: `pyproject.toml` (Python deps), `package.json` (frontend/tooling scripts), `alembic.ini` and `migrations/` for DB.

## Build, Test, and Development Commands

- Backend (API):
  - Create venv + install: `python -m venv .venv && . .venv/bin/activate && pip install -e .`.
  - Run dev server: `uvicorn open_webui.main:app --reload`.
- Frontend (UI):
  - Install: `npm ci`
  - Dev server: `npm run dev` (Vite, fetches Pyodide resources)
  - Build: `npm run build`, preview: `npm run preview`
- Tests (Python):
  - All: `pytest backend/open_webui/test -q`
  - Subset (e.g., routers): `pytest backend/open_webui/test/apps/webui/routers -q`

## Coding Style & Naming Conventions

- Python: Black formatting (`npm run format:backend`), Pylint (`npm run lint:backend`). Use snake_case for modules/functions, PascalCase for classes, 4‑space indents.
- Frontend: Prettier + ESLint (`npm run lint`, `npm run format`). Use kebab-case for files, PascalCase for Svelte components.
- Keep functions small, typed (Pydantic/typing), and avoid side effects in models.

## Testing Guidelines

- Frameworks: Pytest (+ pytest-asyncio), FastAPI `TestClient` for API routes.
- Location/naming: place tests under `backend/open_webui/test`, files `test_*.py`, functions `test_*`.
- Tips: Prefer SQLite `DATABASE_URL` for local runs; isolate via fixtures; mock external services (Redis, S3, OAuth) in unit tests.
- Orchestrator: The test suite is not considered fixed until `backend/open_webui/test/run_tests.sh all` runs without error. Use this script (which applies test-local `pytest.ini` and disables plugin autoload) for final verification.

## Commit & Pull Request Guidelines

- Commits: concise, imperative subject; include scope when helpful (e.g., `routers: add models listing filter`).
- PRs: clear description, linked issues, reproduction steps, and screenshots for UI changes. Include tests for new behavior and migration notes if DB changes.

## Security & Configuration Tips

- Use `.env` for secrets; never commit credentials. Common vars: `DATABASE_URL`, `WEBUI_SECRET_KEY`, `REDIS_URL`.
- `backend/open_webui/env.py` loads and normalizes env; Postgres URLs should use `postgresql://`.
