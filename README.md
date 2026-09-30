<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# PeriHub

[![Pipeline Status](https://img.shields.io/github/actions/workflow/status/PeriHub/PeriHub/CI.yml?branch=main)](https://github.com/PeriHub/PeriHub/actions)
[![docs](https://img.shields.io/badge/docs-v1-blue.svg)](https://perihub.github.io/PeriHub/)
[![License](https://img.shields.io/badge/License-Apache-blue.svg)](https://github.com/PeriHub/PeriHub/blob/main/LICENSE.md)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8159334.svg)](https://doi.org/10.5281/zenodo.8159334)
[![Docker Image](https://img.shields.io/docker/pulls/perihub/frontend)](https://hub.docker.com/r/perihub/frontend)
[![YouTube](https://img.shields.io/youtube/channel/subscribers/UCeky7HtUGlOJ2OKknvl6YnQ)](https://www.youtube.com/@PeriHub)

PeriHub is a web application for setting up, running and analysing peridynamic simulations. You configure a
model in the browser, PeriHub generates the mesh and input deck, and the simulation runs on the
[PeriLab](https://github.com/PeriHub/PeriLab.jl) solver. PeriHub is developed at the German Aerospace Center (DLR).

![PeriHub: model setup on the left, simulation results on the right](docs/assets/images/PeriHub_demo.png)

## What you can do

- **Start from a built-in model** and adjust its parameters, with a live preview of geometry and blocks.
- **Describe your own models** in YAML, or in Python when you need custom logic. See
  [Own models](docs/OwnModels.md).
- **Run simulations** on the bundled PeriLab container or on an external PeriLab server, and follow progress and
  logs while they run.
- **Analyse results** in a 3D viewer, as plots, and with crack analysis.
- **Work in teams:** user accounts, projects, and shared models and materials.
- **Automate** through the REST API. The interactive API docs are at `/docs` on the backend.

## Quick start

You need [Docker](https://docs.docker.com/get-docker/) with Docker Compose.

```bash
git clone https://github.com/PeriHub/PeriHub.git
cd PeriHub
cp .env.example .env
docker compose up
```

Then open http://localhost:8080.

All settings live in `.env`. [`.env.example`](.env.example) documents them. The ones you are most likely to change:
`TRIAL` and `DEPLOYMENT_MODE` (trial, community or enterprise), `DATABASE_URL`, and `SOLVER_BACKEND`. Set
`SOLVER_BACKEND=external` together with `EXTERNAL_PERILAB_URL` to run simulations on your own PeriLab server
instead of the bundled container.

## Documentation

- User guide: https://perihub.github.io/PeriHub/
- Video tutorials: https://www.youtube.com/@PeriHub

## Development

PeriHub has a FastAPI backend (`backend/`) and a SvelteKit frontend (repository root). For development, run both
locally and use Docker only for the database and the solver.

Requirements: Python 3.11, Node.js (LTS, for example via [nvm](https://github.com/nvm-sh/nvm)) and Docker.

1. Start the database and the solver:

   ```bash
   docker compose up perihub_db perilab -d
   ```

2. In `.env`, point the backend at the database:

   ```bash
   DATABASE_URL=postgresql+psycopg://perihub:perihub@localhost:5432/perihub
   ```

3. Install the backend and create the database schema:

   ```bash
   pip install "fastapi[standard]"
   pip install -r backend/requirements.txt -r backend/requirements-dev.txt
   pip install git+https://github.com/JTHesse/crackpy.git
   cd backend && alembic upgrade head
   ```

4. Start the backend. It runs at http://localhost:8000, with API docs at http://localhost:8000/docs:

   ```bash
   cd backend/app
   fastapi dev main.py
   ```

5. Start the frontend. It runs at http://localhost:9000 and forwards `/api` to the backend:

   ```bash
   npm install
   npm run dev
   ```

### Tests and checks

```bash
# Backend (from backend/app)
PYTHONPATH=$(pwd)/../.. python -m pytest tests

# Frontend
npm run lint
npm run check
npm run test:unit
npx playwright test

# Formatting (pre-commit hooks)
pre-commit run --all-files
```

After changing a backend endpoint, regenerate the typed API client while the backend is running:

```bash
npm run client
```

## Citation

If you use PeriHub in your research, please cite it via Zenodo:
[doi.org/10.5281/zenodo.8159334](https://doi.org/10.5281/zenodo.8159334).

## Contact

- [Jan-Timo Hesse](mailto:Jan-Timo.Hesse@dlr.de)

## License

See [LICENSE.md](LICENSE.md) for how the content is licensed.
