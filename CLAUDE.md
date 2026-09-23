# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PeriHub is a web platform for peridynamics simulations: a FastAPI backend (`backend/`) plus a Svelte 5/SvelteKit frontend (repo root — see `MIGRATION.md` for the history of its move from `frontend/app`, a Quasar/Vue 3 app), deployed with docker-compose alongside a `perilab` container that runs the PeriLab.jl solver over SSH.

## Commands

### Full stack

```bash
cp .env.example .env   # configure (TRIAL, CLUSTER_*, KEYCLOAK_*, ...)
docker compose up      # frontend at http://localhost:8080
```

The solver runs in the separate `perihub_perilab` container (SSH, port 22). To submit jobs in dev mode:

```bash
docker compose up perilab -d
```

### Backend

```bash
pip install "fastapi[standard]"
pip install -r backend/requirements.txt
pip install git+https://github.com/JTHesse/crackpy.git   # crack analysis dependency

cd backend/app
fastapi dev main.py        # API at http://localhost:8000, docs at /docs
```

Backend tests (pytest config is in `backend/app/pyproject.toml`; tests import `from backend.app.main` but read fixtures from relative `./models`, so run from `backend/app/` with the repo root on PYTHONPATH):

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
npm run check                # svelte-check (types)
npm run test:unit           # vitest — pure logic (e.g. src/lib/utils/elastic-constants.ts)
npx playwright test         # e2e; builds + previews on :4173 (see playwright.config.ts)
```

Regenerate the typed API client after any backend endpoint change (needs the backend running on :8000):

```bash
npm run client    # writes src/lib/client/ via @hey-api/openapi-ts — never hand-edit those files
```

## Architecture

### Backend (`backend/app`)

- `main.py` — FastAPI app; mounts routers, serves `/assets`, streams job logs over WebSocket `/ws`.
- `routers/` — one module per API tag: `generate` (models/mesh), `model` (model/input-deck CRUD), `upload`, `translate`, `jobs` (run/cancel/status), `results`, `energy`, `delete`, `docs`. Each endpoint sets an `operation_id`; the OpenAPI schema is the contract for the frontend client.
- `support/globals.py` — all configuration comes from env vars loaded from `.env`: `DEV`, `TRIAL`, `MAX_NODES`, `CLUSTER_URL/USER/PASSWORD/JOB_PATH/PERILAB_PATH` (cluster mode enabled when CLUSTER_URL is set).
- `support/file_handler.py` — centralizes everything path- and auth-related: user data lives under `backend/app/simulations/<username>/<model>/<folder>` (mounted volume); usernames come from a Keycloak JWT or, in dev mode, a random guest name. Also owns SSH/SFTP connections (paramiko) to the cluster and to the `perihub_perilab` container.
- `support/writer/` — generates what the solver consumes: `model_writer.py` (input deck), `sbatch_writer.py` (`runPerilab.sh` / sbatch scripts), `yaml_writer_perilab.py`.
- `support/model/` (geometry, meshing, material, rve) and `support/results/` (analysis, crack_analysis).

**Job execution** (`routers/jobs.py`): copies model files (+ user material libs) to either the local `perihub_perilab` container or a remote HPC cluster via SFTP, then writes and launches `runPerilab.sh` there (optionally via `sbatch`). Logs are read back through `/ws`.

**Model generator pattern** — this is the core extensibility mechanism:

- Each built-in model lives in `backend/app/models/<Name>/<Name>.py` exposing a `main` class, next to a `<Name>.json` holding its default `ModelData` config.
- The model file defines a Pydantic `Valves` class whose fields are the UI-exposed parameters; `generate_model` imports `app.models.<Name>.<Name>.main` dynamically, instantiates it with the valve values, and builds geometry/discretization.
- User-supplied models go into `own_models/` (a mounted volume, default `./backend/app/own_models` per `docker-compose.yml`). They are loaded/reloaded via `load_or_reload_main()` and their frontmatter docstring (`title/description/author/requirements/version`) is parsed to register them in the UI; listed `requirements:` are pip-installed at startup when `FRONTMATTER_INSTALLATION` isn't False.

### Frontend (repo root)

Svelte 5 (runes) + SvelteKit + TypeScript + Tailwind v4 + `bits-ui`/shadcn-svelte, no Pinia
(stores are plain `$state` classes) and no vue-i18n (uses `sveltekit-i18n` instead).

- `src/lib/client/` — generated axios client mirroring the backend OpenAPI schema; components/stores call these services directly. Never hand-edit — regenerate with `npm run client`.
- `src/routes/perihub/+page.svelte` is the main workflow page; `src/lib/components/expansions/` each map to one input-deck section (Discretization, BoundaryConditions, Material, Blocks, Output, ...), `src/lib/components/views/` hold the viewers (VTK mesh, Plotly plots, text editor, log view, results).
- `src/lib/stores/` — `auth-store` (Keycloak login, bootstrapped in `src/lib/auth/keycloak.ts`), `model-store`, `view-store`, `default-store`. All are `*.svelte.ts` files exporting a singleton instance of a class with `$state` fields — import the instance, mutate its fields directly (deep reactivity works on nested objects/arrays without extra plumbing).
- `src/lib/config.ts` — runtime config; in prod, values are `_VALUE` placeholders substituted by `entrypoint.sh` at container startup (same mechanism as before, just pointed at the new build output path).
- Pure, testable logic (e.g. `src/lib/utils/elastic-constants.ts`) is kept out of `.svelte` files where practical — see `PROFESSIONALIZATION.md` for the rationale and what else is a good candidate.
- Known gaps: `ModelView`/`ResultsView` (VTK.js 3D viewers) and a few advanced `ViewActions` dialogs are still `PendingMigration` placeholders — see `MIGRATION.md`.

### Versioning & release

The version lives in three places that must be kept in sync: `backend/app/pyproject.toml`, `main.py`'s `FastAPI(version=...)`, and `package.json` (repo root). Tagging `vX.Y.Z` triggers the Deploy workflow, which reads the version from `pyproject.toml` and pushes `perihub/backend` / `perihub/frontend` images to Docker Hub.

### Conventions

- Every source file carries SPDX headers (`SPDX-FileCopyrightText: 2023 PeriHub ...` / `SPDX-License-Identifier: Apache-2.0`); binary/non-text files use sidecar `.license` files. Follow this for new files.
- Python: black + isort (profile black), max line length 120; flake8 config in `pyproject.toml` (pflake8). `dev_models/` is excluded from formatting/tests.
