#!/bin/sh
# Backend dev server on :8000. Unlike `fastapi dev`, it reloads only on code changes: watching all of backend/app
# also catches simulation output, own models and guest cleanup, and every reload waits for the frontend's open log
# stream to close - the server then hangs. Changes to main.py need a manual restart.
cd "$(dirname "$0")/app" && exec python3 -m uvicorn app.main:app --app-dir .. --port 8000 --reload \
  --reload-dir routers --reload-dir support --reload-dir db --reload-dir ee \
  --timeout-graceful-shutdown 3 "$@"
