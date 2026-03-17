# Changelog

All notable changes to this project will be documented in this file.

This project follows an evolving architecture from MVP to Enterprise SaaS.

## [0.3.0]

### Added

- **Multi-Tenant Async Ingestion**: Transitioned from synchronous processing to an event-driven architecture using Redis as a Message Broker.
- **Tenant Identification (Security)**: Implemented verify_api_key middleware in apps/server/src/core/auth.py to validate X-API-KEY against a tenant catalog before processing.
- **Asynchronous Hand-off**: Integrated FastAPI BackgroundTasks to decouple ingestion from processing, allowing immediate 202 Accepted responses.
- **Redis Integration**: Added ingestion.py service to package and push events (lpush) to the events_queue in Redis.
- **Dedicated Worker Service**: Created a standalone Worker engine (apps/server/src/workers/main.py) using brpop for efficient, non-blocking event consumption.
- **Monorepo Manifest**: Configured pyproject.toml using setuptools to manage the apps/ namespace and ensure consistent internal imports.

### Infrastructure
- **Service Decoupling**: Updated docker-compose.yml to include the worker service as an independent scaling unit.
- **Hardened Docker Image**: Refactored Dockerfile to use uv for deterministic dependency resolution and /opt/venv for immutable runtime environments.
- **Observability**: Enabled PYTHONUNBUFFERED=1 in containers to ensure real-time log streaming from background workers.

### DevOps
- **Semantic Security**: Refactored error handling to return 401 Unauthorized for authentication failures, reserving 422 strictly for Pydantic schema validation.
- **Architectural Evolution**: Established the foundation for horizontal scaling (adding more workers) without modifying the API ingestion logic.

## [0.2.0]

### Added

- **Multi-Service Orchestration**: Integrated docker-compose.yml to manage FastAPI, PostgreSQL 16, and Redis 7 services.
- **Advanced Dockerization**: Implemented Multi-stage builds to optimize image size and security.
- **Configured Non-root user** (appuser) execution for container hardening.
- **Persistent Storage**: Configured Docker volumes for PostgreSQL to ensure data persistence across container restarts.
- **Network Isolation**: Created a dedicated bridge network (backend_internal) to isolate database and cache traffic from the public network.
- **Environment Management**: Added .dockerignore to keep the build context clean and secure.

### Infrastructure

- **Database**: PostgreSQL 16 official image for the storage layer.
- **Cache**: Redis 7 Alpine-based image for high-performance caching.
- **Service Discovery**: Automatic DNS-based communication between containers (e.g., db:5432).

### DevOps

- **Hardening**: Applied the principle of least privilege within the runtime container.
- **Efficiency**: Reduced attack surface and build times using the builder pattern in Docker.
- **Portability**: Transitioned from "works on my machine" to a fully reproducible containerized stack.

## [0.1.0]

### Added

- **FastAPI Base**: Initial skeleton with a functional health check endpoint (`/health`) for availability monitoring.
- **Modular Structure**: Repository organization under `apps/server/src` to support service scalability.
- **Modular directory structure**
- **Code Quality Automation**: Configuration of `.pre-commit-config.yaml` integrating `black`, `flake8`, and `isort`.
- **Project Governance**: Technical `README.md`, professional `.gitignore`, and `requirements.txt` for dependency management.

### Infrastructure

- **Dev Environment**: Python 3.12 virtual environment setup and dependency isolation.
- **Baseline**: Created Git Tag `v0.1.0` to establish the architectural starting point.

### DevOps

- **Shift-Left Validation**: Activated pre-commit hooks to enforce PEP8 standards and formatting before each commit.
- **Automation**: Integrated automatic validation for structural files (YAML, JSON) via pre-commit hooks.

---

## Versioning Strategy

This project follows semantic versioning:

**MAJOR.MINOR.PATCH**

Example:

**1.0.0**

- **Major** → Architecture changes  
- **Minor** → New features  
- **Patch** → Fixes
