# Realtime SaaS Platform

## Project Overview

Multi-tenant webhook ingestion platform designed using event-driven architecture and DevOps best practices.

## Architecture
```
Client → FastAPI (Container) → Redis (Cache) → PostgreSQL (Database)
```

### Production Equivalent (AWS)
```
ALB → ECS Fargate → ElastiCache → RDS
```

## Tech Stack

- Framework: FastAPI (Python 3.12)
- Database: PostgreSQL 16
- Cache/Queue: Redis 7
- Containerization: Docker (Multi-stage builds)
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

## Local Development (Optional)

Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies
```bash
pip install -r apps/server/requirements.txt pre-commit
pre-commit install
```

Run application
```bash
uvicorn main:app --app-dir apps/server/src --reload
```

## Repository Structure
```
.
├── apps
│   └── server
│       ├── requirements.txt
│       └── src
│           └── main.py       # FastAPI Entrypoint
├── docker
│   └── Dockerfile            # Multi-stage & Non-root build
├── .dockerignore
├── .pre-commit-config.yaml   # Code Quality Automation
├── docker-compose.yml        # Infrastructure Orchestration
├── CHANGELOG.md
└── README.md
```

## Changelog

See [Changelog](CHANGELOG.md)
