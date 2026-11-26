# JobOrbit

Personal, self-hosted job discovery and application tracking with country opportunity and
eligibility intelligence. Single user, runs on your own machine. Specifications live in
[`docs/`](docs/).

## Requirements

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 22+ and npm
- Optional: Docker, for the PostgreSQL dev database

## Run locally (development)

```bash
# 1. Backend API on http://127.0.0.1:8765 (Swagger UI at /docs)
cd backend
uv sync
uv run joborbit dev        # applies migrations, loads reference data, starts with auto-reload

# 2. Frontend on http://localhost:5173 (proxies /api to :8765)
cd frontend
npm install
npm run dev
```

Open the frontend, choose a password and complete the setup screen.

## Run as a single app

```bash
cd frontend && npm run build          # writes frontend/dist
cd ../backend && uv run joborbit migrate && uv run joborbit-api
```

The API serves the built app at http://127.0.0.1:8765. To expose it beyond this machine, put a
TLS reverse proxy in front (see [`deploy/Caddyfile`](deploy/Caddyfile)) and set
`JOBORBIT_HTTPS_TERMINATED=true`; the app refuses to listen on a non-loopback address over plain
HTTP otherwise. A systemd example is in [`deploy/joborbit.service`](deploy/joborbit.service).

## Configuration

Copy [`backend/.env.example`](backend/.env.example) to `backend/.env`. All settings are optional;
data (SQLite database, logs) goes to `backend/data/` by default.

## PostgreSQL (optional)

```bash
docker compose -f deploy/postgres.compose.yml up -d   # 127.0.0.1:55432, user/password/db: joborbit
export JOBORBIT_DATABASE_URL=postgresql+psycopg://joborbit:joborbit@127.0.0.1:55432/joborbit
cd backend && uv run joborbit migrate
```

These credentials are for local development only.

## Tests and checks

```bash
cd backend
uv run ruff check . && uv run ruff format --check . && uv run mypy .
uv run pytest                                    # SQLite
JOBORBIT_TEST_POSTGRES_URL=postgresql+psycopg://joborbit:joborbit@127.0.0.1:55432/joborbit uv run pytest

cd frontend
npm run lint && npm test && npm run build
```

CI runs the same checks: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Layout

| Path | What |
|---|---|
| `backend/core/` | Config, database, errors, logging, middleware, pagination, SPA serving |
| `backend/auth/` | Password, sessions, CSRF, login throttling |
| `backend/app_settings/`, `backend/user_profile/` | Settings and profile APIs |
| `backend/catalog/` | Countries, regions, skills (reference data in `catalog/data/`) |
| `backend/ingestion/` | Job source and sync log models (adapters arrive in Phase 2) |
| `backend/migrations/` | Alembic migrations |
| `frontend/src/components/` | Shared components (one folder each, with `index.ts`) |
| `frontend/src/pages/` | One folder per page; page-only components in its `components/` |
| `deploy/` | PostgreSQL compose file, Caddy and systemd examples |
