.PHONY: up down logs log migrate rollback seed lint format

# --- Dev Environment ---
up:
	docker compose up --build -d
down:
	docker compose down
logs log:
	docker compose logs -f

# --- Database ---
migrate:
	docker compose exec api alembic -c infra/alembic.ini upgrade head
rollback:
	docker compose exec api alembic -c infra/alembic.ini downgrade -1
seed:
	docker compose exec api python infra/migrations/seeds/seed_tenants.py

# --- Quality ---
lint:
	uv run ruff check .
format:
	uv run ruff format .

# --- Testing ---
# test:
#    uv run pytest
