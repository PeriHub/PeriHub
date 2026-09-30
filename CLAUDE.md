# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PeriHub is a web platform for peridynamics simulations: a FastAPI backend (`backend/`) plus a Svelte 5/SvelteKit frontend (repo root), deployed with docker-compose alongside a Postgres database (`perihub_db`) and a `perilab` container that runs the PeriLab.jl solver behind the PeriLab HTTP API.

## Commands

### Full stack

```bash
cp .env.example .env   # configure (DATABASE_URL, SESSION_SECRET, GUEST_ACCESS, SOLVER_BACKEND, OAUTH_*, LICENSE_*, ...)
docker compose up      # frontend at http://localhost:8080
```

To submit jobs in dev mode, start the DB and solver (PeriLab API is published on host port 3000, matching the `LOCAL_PERILAB_API_URL` default):

```bash
docker compose up perihub_db perilab -d
```

### Backend

```bash
pip install "fastapi[standard]"
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
pip install git+https://github.com/JTHesse/crackpy.git   # crack analysis dependency

cd backend && alembic upgrade head   # create/migrate the DB schema (needs DATABASE_URL)

cd backend/app
fastapi dev main.py        # API at http://localhost:8000, docs at /docs
```

Schema changes go through Alembic (`backend/alembic/versions/`); ORM models are in `backend/app/db/models.py`.

Backend tests (pytest config is in the root `pyproject.toml`; tests import `from backend.app.main` but read fixtures from relative `./models`, so run from `backend/app/` with the repo root on PYTHONPATH):

```bash
cd backend/app
PYTHONPATH=$(pwd)/../.. python -m pytest tests/unit/test_main.py              # single test file
PYTHONPATH=$(pwd)/../.. python -m pytest tests/unit/test_main.py::test_generate_model -v  # single test
PYTHONPATH=$(pwd)/../.. python -m pytest tests                                # all (unit + image_export)
```

Formatting/linting (enforced by pre-commit, line length 120):

```bash
pre-commit run --all-files    # or: black . && isort --profile black .
```

### Frontend

```bash
npm install
npm run dev                 # http://localhost:9000, proxies /api to :8000
npm run lint                # eslint
npm run format              # prettier
npm run check               # svelte-check (types)
npm run test:unit           # vitest — test/unit/**, pure logic (e.g. src/lib/utils/elastic-constants.ts)
npx playwright test         # e2e in test/e2e; builds + previews on :4173 (see playwright.config.ts)
```

Regenerate the typed API client after any backend endpoint change (needs the backend running on :8000):

```bash
npm run client    # writes src/lib/client/ via @hey-api/openapi-ts — never hand-edit those files
```

## Architecture

### Backend (`backend/app`)

- `main.py` — FastAPI app; mounts routers, serves `/assets`, `/health`. Lifespan installs own-model requirements and checks the DB connection.
- `routers/` — one module per API tag. Simulation: `generate` (models/mesh), `model` (model/input-deck CRUD), `upload`, `translate`, `jobs` (run/cancel/status, run listing, `/{run_id}/log`), `results`, `energy`, `delete`, `docs`. Platform: `auth` (local email/password), `oauth` (OIDC), `config` (`GET /config/public`), `library` (shared model configs/materials), `projects`, `teams`, `usage`, `license`. Each endpoint sets an `operation_id`; the OpenAPI schema is the contract for the frontend client.
- `support/globals.py` — all configuration comes from env vars loaded from `.env` (`.env.example` documents them): `GUEST_ACCESS`, `DEPLOYMENT_MODE` (community/enterprise), `MAX_NODES`, `DATABASE_URL`, `SESSION_SECRET`, `API_KEYS`, `SOLVER_BACKEND`/`LOCAL_PERILAB_API_URL`/`EXTERNAL_PERILAB_URL`, job limits (`MAX_CONCURRENT_LOCAL_JOBS`, `MAX_CONCURRENT_JOBS_PER_USER`), `OAUTH_*`, `LICENSE_*`.
- `db/` — SQLAlchemy engine/session (`base.py`, `get_db` dependency) and ORM models (`models.py`: Organization, User, OAuthIdentity, AdminSetting, Team, Project, JobQueueEntry, ModelConfig, Material). Accounts (including guests), sharing and job submission require it.
- `support/file_handler.py` — path handling: user data lives under `backend/app/simulations/<username>/<model>/<folder>` (mounted volume).
- **Identity/auth** — `support/db_auth.resolve_user()` resolves the caller in order: `X-Api-Key` (`api_key_auth.py`) → `Authorization: Bearer` local-session JWT (`local_auth.py`) → legacy `userName` header (OAuth, via `FileHandler.get_user_name()`). Not all routers are migrated to `resolve_user()` yet. `rbac.py` has ranked roles (admin > developer > member > viewer > guest; only developer/admin may create/edit/delete own models and save default configs, since models run server-side code and configs are shared; the editor offers saving built-in defaults only under `npm run dev`) and visibility-scoped queries (private/team/org/public); `entitlements.py` + `license_client.py` gate features by license (nothing is gated when no license server is configured); `seats.py` and `audit_log.py` round this out; `/usage` aggregates `JobQueueEntry` rows. `guest.py` holds guest restrictions/limits (guest access: anonymous visitors get a `guest` account via `POST /auth/guest`), `guest_sweeper.py` stops overdue guest jobs and deletes expired guests.
- `support/writer/` — generates what the solver consumes: `model_writer.py` (input deck), `yaml_writer_perilab.py`.
- `support/model/` (model API, shapes, YAML models, loader, meshing — see below) and `support/results/` (analysis, crack_analysis).

**Job execution** (`routers/jobs.py`): `support/solver_backend.py` submits to a PeriLab HTTP API via `support/perilab_api_client.py`. `SOLVER_BACKEND=local` = the bundled `perihub_perilab` container sharing the simulations volume (files read directly); `external` = a customer-hosted PeriLab API (files uploaded/downloaded through it). Capacity and per-user caps are checked up front (`job_concurrency.py`, 429 if exceeded — there is no queue), and each submission is recorded as a `JobQueueEntry` holding `perilab_job_id` (`job_queue.py`), so **local submission requires `DATABASE_URL`**. Logs/status are fetched from the PeriLab API. There is no HPC/cluster (SFTP/sbatch) path anymore.

**Model generator pattern** — this is the core extensibility mechanism (reference: `docs/OwnModels.md`):

- A model is a folder `backend/app/models/<Name>/` (built-in) or `own_models/<Name>/` (mounted volume, default `./backend/app/own_models`) holding **one** generator — `<Name>.yaml` (no-code) or `<Name>.py` (a `PeriHubModel` subclass) — plus an optional `<Name>.json` default `ModelData` config and, for YAML models, an optional `analysis.py`. Built-ins win over own models of the same name.
- `support/model/loader.py` is the only place that knows this layout: `load_model()`, `load_source()` (unsaved YAML, preview only), `load_analyses()`, `list_models()`. Python files are loaded by path (fresh each call) and import the public API as `from perihub import ...` (registered by the loader); metadata is read statically (YAML / `ast`) so listing and `requirements:` installation at startup never import user code.
- `support/model/model_api.py`: `PeriHubModel` (`Param` class attributes → UI valves, `geometry()` → `Shape`, `blocks()`, optional `spacing`/`grid_origin()`/`points()`/`edit_model_data()`), `build()` (points on a grid inside the shape, block ids, shape outlines + per-block bounds for the preview), `@analysis` + `AnalysisContext`. `shapes.py`: numpy inside-tests (`box sphere ellipsoid cylinder cone polygon`, `+ - &`). `yaml_model.py` turns YAML into a `PeriHubModel` subclass; `expr.py` evaluates its expressions via an AST whitelist.
- Result images: `@analysis` functions, listed by `GET /models/{name}/analyses`, run by `POST /results/analysis` (returns PNG), triggered from `ViewActions.svelte` and shown in `AnalysisView.svelte`.
- `tests/unit/test_model_regression.py` pins the built-in models to the output of the pre-conversion generators (fixtures in `tests/unit/fixtures/model_regression/`).

### Frontend (repo root)

Svelte 5 (runes) + SvelteKit (`adapter-static`) + TypeScript + Tailwind v4 + `bits-ui`/shadcn-svelte, no Pinia
(stores are plain `$state` classes), i18n via `sveltekit-i18n` (`src/lib/i18n/`).

- `src/lib/client/` — generated axios client mirroring the backend OpenAPI schema; components/stores call these services directly. Never hand-edit — regenerate with `npm run client`.
- `src/routes/perihub/+page.svelte` is the main workflow page; `src/lib/components/expansions/` each map to one input-deck section (Discretization, BoundaryConditions, Material, Blocks, Output, ...), `src/lib/components/views/` hold the viewers (model/results 3D views, charts, text editor, log view, `JobsView`), `dialogs/` hold e.g. `UserSettingsDialog`.
- `src/lib/stores/` — `auth-store`, `model-store`, `view-store`, `default-store`. All are `*.svelte.ts` files exporting a singleton instance of a class with `$state` fields — import the instance, mutate its fields directly (deep reactivity works on nested objects/arrays without extra plumbing).
- `src/lib/config.ts` — `config` holds only build-time values (`dev`, `apiBase`); everything deployment-specific (`guest_access`, `guest_limits`, `oauth_enabled`, `deployment_mode`) is fetched at startup from the backend's `GET /config/public` into `publicConfig` via `loadPublicConfig()`. There is no longer any build-time placeholder substitution — `entrypoint.sh` just starts nginx.
- `src/lib/auth/oauth.ts` — `initAuth()` (awaits `loadPublicConfig()` first), generic OAuth2/OIDC login for any IdP (Keycloak included), guest session via `POST /auth/guest` when guest access is on.
- Pure, testable logic (e.g. `src/lib/utils/elastic-constants.ts`) is kept out of `.svelte` files where practical, with tests in `test/unit/`.

### Versioning & release

The version lives in three places that must be kept in sync: the root `pyproject.toml`, `backend/app/main.py`'s `FastAPI(version=...)`, and `package.json` (repo root). Tagging `vX.Y.Z` triggers the Deploy workflow, which reads the version from `pyproject.toml` and pushes `perihub/backend` / `perihub/frontend` images to Docker Hub.

### Conventions

- Every source file carries SPDX headers (`SPDX-FileCopyrightText: 2023 PeriHub ...` / `SPDX-License-Identifier: Apache-2.0`); binary/non-text files use sidecar `.license` files. Follow this for new files.
- Python: black + isort (profile black), max line length 120; flake8 config in the root `pyproject.toml` (pflake8).
- New backend modules carry a module docstring explaining the "why" and the roadmap phase (Phase 0/1/2) — read these first; they're the best documentation of the multi-user/auth/job design.
