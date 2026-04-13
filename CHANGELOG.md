# Changelog

All notable changes to this project will be documented in this file.

This project follows an evolving architecture from MVP to Enterprise SaaS.

## [0.7.0]

### Added
- **Managed PostgreSQL (AWS RDS)**: Provisioned RDS PostgreSQL 16 Single-AZ (`db.t3.micro`, 20GB gp3) in private VPC subnets via a reusable `modules/rds` Terraform module.
- **DB Subnet Group**: Anchors the RDS instance exclusively to private subnets, making a public endpoint structurally impossible regardless of Security Group configuration.
- **Least-Privilege Security Groups**: Implemented SG-to-SG firewall model — `rds_sg` accepts port 5432 only from `app_sg`, with no CIDR-based rules that could allow unintended access as instance IPs rotate.
- **Application Security Group (`app_sg`)**: Placeholder Security Group created in the RDS module and exported as an output; EC2 (Hito 8) will adopt it without requiring changes to the RDS configuration.
- **Automated Backups**: Daily snapshots at 03:00–04:00 UTC with 7-day retention, maintenance window at 04:00–05:00 UTC (post-backup).
- **Encrypted Storage**: `storage_encrypted = true` with AWS-managed KMS key applied to the gp3 volume.
- **Sensitive Variable Handling**: `db_password` declared with `sensitive = true` and injected via `TF_VAR_db_password` — never hardcoded or committed.

### Infrastructure
- **New Terraform Module**: `infra/terraform/modules/rds/` with `main.tf`, `variables.tf`, and `outputs.tf`.
- **Environment Updated**: `infra/terraform/envs/dev/main.tf` calls the `rds` module consuming `vpc_id` and `private_subnet_ids` from the `networking` module outputs.
- **New Outputs**: `db_endpoint`, `db_host`, `db_port`, `db_name`, `app_security_group_id`, `rds_security_group_id` exported from `envs/dev`.

## [0.6.0]

### Added
- **Cloud Network Backbone**: Provisioned multi-AZ AWS VPC (`10.0.0.0/16`) with 2 public and 2 private subnets distributed across `us-east-1a` and `us-east-1b`.
- **Internet Gateway**: Enabled inbound/outbound public traffic for resources in public subnets (future ALB placement).
- **NAT Gateway + Elastic IP**: Enabled outbound internet access from private subnets without exposing internal resources.
- **Route Tables**: Defined explicit public (`0.0.0.0/0 → IGW`) and private (`0.0.0.0/0 → NAT`) routing rules with subnet associations.
- **Reusable Terraform Module**: Implemented `infra/terraform/modules/networking` as a parameterized, environment-agnostic module (CIDRs, AZs, project name, environment as variables).
- **Remote State Backend**: Configured Terraform state storage in S3 with DynamoDB locking for concurrent-safe team collaboration.
- **FinOps Tagging**: Applied `default_tags` at provider level (`Project`, `Environment`, `ManagedBy`) for cost attribution across all resources.

### Infrastructure
- **IaC Toolchain**: Terraform 1.14.7 with AWS provider `~> 6.37` introduced as the standard for all cloud resource provisioning.
- **Environment Structure**: Established `infra/terraform/envs/dev/` as the entry point pattern for multi-environment deployments (dev → staging → prod).

## [0.5.0]

### Added
- **Continuous Integration Pipeline**: Implemented three-stage GitHub Actions workflow (`code-quality → test → docker-build`) with cascading job dependencies enforcing fail-fast validation on every Pull Request.
- **Unit Test Suite**: Implemented 10 unit tests across `test_auth.py` and `test_webhooks.py` covering tenant authentication middleware and webhook ingestion endpoint using `dependency_overrides` and `patch()`.
- **Coverage Gate**: Configured `pytest-cov` with a 70% minimum threshold enforced at merge time via `--cov-fail-under=70` and `[tool.coverage.run]` source declaration.
- **Test Environment Bootstrap**: Added `conftest.py` with `os.environ.setdefault` to inject `DATABASE_URL` and `REDIS_URL` before module collection, preventing `create_engine(None)` failure in CI.
- **Docker Build Validation**: Added dry-run Docker Buildx step targeting the `runner` production stage, catching image compilation errors before any cloud deployment attempt.

### Changed
- **Dependency Manifest**: Added `httpx`, `pytest-cov`, and `ruff` to `[project.optional-dependencies] dev` in `apps/api/pyproject.toml`.

## [0.4.0]

### Added
- **Infrastructure-as-Code (Schema)**: Initialized database migration lifecycle using Alembic for declarative schema management.
- **Relational Domain Model**: Implemented decoupled domain entities (`Tenant`, `Message`) with SQLAlchemy 2.1.
- **Service Decoupling**: Refactored monolithic structure into a scalable Monorepo (apps/libs/infra).
- **Control Plane**: Integrated `Makefile` as a standardized interface for local orchestration and lifecycle management.

### Changed
- **Worker Resiliency**: Optimized model discovery during event processing via centralized metadata registration.
- **Dependency Management**: Standardized build environment using `uv` for deterministic runtime isolation.

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
