# Realtime SaaS Platform

## Project Overview

Multi-tenant webhook ingestion platform designed using event-driven architecture and DevOps best practices.

## Architecture
```
Client → FastAPI (Pydantic Validation) → Redis (In-memory Queue) → Worker (Background Tasks) → PostgreSQL
```

### Production Equivalent (AWS)
```
ALB → ECS Fargate (API/Worker) → ElastiCache (Redis) → RDS (PostgreSQL)
```

## Tech Stack

- Framework: FastAPI (Python 3.12)
- Package Manager: uv
- Database: PostgreSQL 16
- Cache/Queue: Redis 7
- Containerization: Docker (Multi-stage, Non-root, Hardened .venv)
- Orchestration: Docker Compose
- Quality: Pre-commit (Black, Flake8, isort)

## Quick Start

Start platform
```bash
docker compose up --build
```

Verify services
```bash
docker compose ps
```

## API Documentation

Interactive API documentation available at:
```
http://localhost:8000/docs
```

## Local Development (optional)

Install uv (Standalone recommended)
```bash
# High-performance, no-python-needed install
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Ubuntu optional
sudo snap install astral-uv --classic
```

Initialize environment with `uv`
```bash
# Create .venv and install full dev environment
uv sync

# Install the project in editable mode to resolve namespaces
pip install -e .
```

Install quality tools
```bash
uv run pre-commit install
```

Run services (in separate terminals)
```bash
# Run API (Development mode with reload)
uv run uvicorn apps.server.src.main:app --reload

# Run Worker
uv run python -m apps.server.src.workers.main
```

## Repository Structure
```
.
├── apps
│   └── server
│       └── src
│           ├── api
│           │   └── v1
│           │       ├── auth.py       # API Key & Tenant Logic
│           │       ├── routes.py     # Webhook Endpoints
│           │       └── schemas.py    # Pydantic Models
│           ├── workers
│           │   └── main.py           # Background Processor
│           ├── config.py             # Environment Settings
│           └── main.py               # FastAPI Entrypoint
├── docker
│   └── Dockerfile            # Hardened Multi-stage (uv-based)
├── pyproject.toml            # Project metadata & dependencies
├── uv.lock                   # Deterministic lockfile (TOML)
├── .dockerignore
├── .pre-commit-config.yaml   # Code Quality Automation
├── docker-compose.yml        # Infrastructure Orchestration
├── CHANGELOG.md
└── README.md
```

## Changelog

See [Changelog](CHANGELOG.md)
