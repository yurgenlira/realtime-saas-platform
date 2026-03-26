#!/bin/bash
set -euo pipefail

echo "Running Alembic migrations..."
cd /app
uv run alembic -c infra/alembic.ini upgrade head

echo "Starting Uvicorn..."
exec uv run uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2
