# 🚀 Realtime SaaS Platform

Multi-tenant webhook ingestion platform designed using event-driven architecture and DevOps best practices.

## 🏗️ Architecture
```text
Client → FastAPI (Pydantic Validation) → Redis (In-memory Queue) → Worker (Background Tasks) → PostgreSQL
```

### ☁️ Production Equivalent (AWS)
```text
ALB → ECS Fargate (API/Worker) → ElastiCache (Redis) → RDS (PostgreSQL)
```

## 🛠️ Tech Stack
- **Runtime**: Python 3.12 (uv managed)
- **Framework**: FastAPI
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Containerization**: Docker (Multi-stage, Non-root)
- **Orchestration**: Docker Compose
- **Quality**: Ruff, Pre-commit
- **Testing**: Pytest, pytest-cov (70% minimum coverage gate)
- **CI**: GitHub Actions (lint → test → docker build)

## ⚡ Operational Quick Start

### 1. Provision Infrastructure
Ensure you have a `Makefile` compatible environment and `uv` installed. This command will bootstrap the local containers:

```bash
make up
```

### 2. Database Governance
Apply versioned migrations and seed initial tenant profiles:

```bash
make migrate
make seed
```

### 3. Verify Ingestion
Test the platform using a standard tenant API Key:

```bash
curl -X POST http://localhost:8000/v1/webhooks/ingest \
  -H "x-api-key: key-client-a" \
  -H "Content-Type: application/json" \
  -d '{"provider": "whatsapp", "provider_id": "msg_001", "content": {"text": "ping"}}'
```

### 4. Run Tests
```bash
cd apps/api && uv run pytest tests/unit/ -v
```

## 📁 Project Organization
```text
.
├── apps/               # Scalable service containers (API, Worker)
├── libs/               # Shared domain logic & ORM models (domain package)
├── infra/              # Database migrations & provider configs
├── docker/             # Hardened container definitions
└── Makefile            # Service orchestration interface
```

---
*Detailed documentation for security policies and CI/CD can be found in the [docs](./docs) directory.*

## 📝 Changelog

See [Changelog](CHANGELOG.md)