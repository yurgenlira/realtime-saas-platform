# Changelog

All notable changes to this project will be documented in this file.

This project follows an evolving architecture from MVP to Enterprise SaaS.

## [0.11.0]

### Added
- `apps/api`, `apps/worker`: `boto3>=1.42.89` added to both package dependencies via `uv add`; `uv.lock` regenerated
- `modules/ec2/main.tf`: inline IAM policy `sqs_send_receive` scoped to `sqs_queue_arn` — grants `SendMessage`, `ReceiveMessage`, `DeleteMessage`, `GetQueueAttributes`, `ChangeMessageVisibility` to the EC2 Instance Profile

### Changed
- `apps/api/src/api/services/ingestion.py`: replaced Redis `lpush` with synchronous `boto3.sqs.send_message`; `tenant_id` sent as `MessageAttribute` outside body; SQS client initialized at module level for connection reuse
- `apps/api/src/api/v1/routes.py`: removed `BackgroundTasks` dependency; `push_to_queue` called synchronously — `202` returned only after SQS confirms receipt
- `apps/worker/main.py`: rewrote Redis `brpop` blocking loop as SQS long-polling (`WaitTimeSeconds=20`, `MaxNumberOfMessages=10`) with atomic ACK — `delete_message` called only after `db.commit()`; on exception message re-queues after `visibility_timeout`
- `apps/api/tests/conftest.py`: replaced `REDIS_URL` env var with `SQS_QUEUE_URL` and `AWS_REGION`
- `apps/api/tests/unit/test_webhooks.py`: renamed `test_background_task_is_called_after_202` → `test_push_to_queue_is_called_on_ingest`
- `docker/Dockerfile`: runner stage adds `COPY apps/worker/main.py /app/apps/worker/main.py` so the worker script exists in the production image
- `modules/ec2/user_data.sh`: removed `REDIS_URL` from `.env` heredoc; added worker container launch with `--entrypoint /opt/venv/bin/python`
- `modules/ec2/variables.tf`: added `sqs_queue_arn`; removed `redis_url`
- `modules/ec2/main.tf`: removed `redis_url = var.redis_url` from `templatefile` inputs
- `envs/dev/main.tf`: wired `sqs_queue_arn = module.sqs.ingestion_queue_arn` in `module.ec2`
- `.github/workflows/cd.yml`: added worker `stop → rm → run` with `--entrypoint /opt/venv/bin/python` to SSM RunCommand deploy step

### Removed
- `apps/api/pyproject.toml`, `apps/worker/pyproject.toml`: `redis>=7` removed from both package dependencies
- `envs/dev/variables.tf`: `variable "redis_url"` removed

## [0.10.0]

### Added
- `modules/sqs`: Standard SQS ingestion queue with 30s visibility timeout and 4-day retention
- `modules/sqs`: Dead Letter Queue with 14-day retention and Redrive Policy (`maxReceiveCount: 5`)
- `modules/secrets_manager`: Secrets Manager secret storing RDS credentials as structured JSON (username, password, host, port, dbname)
- `modules/ec2`: IAM inline policy `secrets_manager_read` scoped to exact secret ARN
- `envs/dev`: Variables `db_name` and `redis_url` declared in `variables.tf`

### Changed
- `modules/ec2/user_data.sh`: replaced plaintext `db_password` interpolation with `aws secretsmanager get-secret-value` at boot; added `jq` to package install; added `unset` of credential variables post-write; added `SQS_QUEUE_URL` to `/opt/app/.env`
- `modules/ec2/main.tf`: `user_data` → `user_data_base64`; added `secrets_manager_read` policy; updated `templatefile` inputs
- `envs/dev/main.tf`: wired `module.sqs` and `module.secrets_manager`; replaced `db_*` inputs in `module.ec2` with `rds_secret_arn`, `rds_secret_name`, `sqs_queue_url`, `redis_url`

### Removed
- `modules/ec2/variables.tf`: `db_host`, `db_port`, `db_name`, `db_username`, `db_password` — no longer passed to EC2 module

## [0.9.0]

### Added
- **ECR Repository**: Private Docker registry (`realtime-saas-api`) with `scan_on_push` and lifecycle policy retaining the last 10 images.
- **IAM OIDC Provider + GitHub Actions Role**: Keyless AWS authentication — GitHub signs a JWT per job; AWS validates via OIDC and returns short-lived STS credentials. No static Access Keys stored in GitHub Secrets.
- **CD Workflow (`cd.yml`)**: On merge to `main`: build Docker image → push to ECR with `$GITHUB_SHA` tag + `latest` → SSM RunCommand deploy on EC2. `concurrency: cancel-in-progress: false` serializes deploys to prevent race conditions on `docker stop/run`.
- **Terraform Plan in CI**: Job added to `ci.yml` that runs `terraform init + plan` on every PR touching `.tf` files and posts the output as a PR comment.

### Changed
- **EC2 Instance Profile**: Added `ecr-pull` policy so the instance can `docker pull` from ECR using its IAM role without registry credentials.
- **`user_data.sh`**: Added `chmod 600 / chown ec2-user` on `/opt/app/.env` to restrict credential file access to the process owner.
- **`ci.yml`**: Added `set -o pipefail` to Terraform Plan step so terraform exit codes propagate through the `| tee` pipe.

### Infrastructure
- **New modules**: `infra/terraform/modules/ecr/`, `infra/terraform/modules/iam_github_oidc/`
- **`envs/dev`**: Variables `github_repo`, `terraform_state_bucket`, `terraform_lock_table` added with defaults; outputs `ecr_repository_url`, `github_actions_role_arn` exported.
- **Branch protection**: Required checks `Code Quality`, `Unit Tests`, `Docker Build Check`, `Terraform Plan` enforced on `main`.

## [0.8.0]

### Added
- **EC2 Compute Layer**: Provisioned `t3.micro` (Amazon Linux 2023) in private VPC subnets with `app_sg` attached, enabling connectivity to RDS on port 5432.
- **IAM Instance Profile**: Created IAM Role with `CloudWatchAgentServerPolicy` and `AmazonSSMManagedInstanceCore` — enables CloudWatch Logs and SSH-less access via SSM Session Manager without opening port 22.
- **Docker Bootstrapping via `user_data`**: `templatefile()` renders a bash script that installs Docker, clones the repository (with GitHub PAT for private repo simulation), builds the multi-stage image and launches the API container with RDS credentials injected from Terraform variables.
- **Alembic Entrypoint (`entrypoint.sh`)**: Shell script as Docker `ENTRYPOINT` that runs `alembic upgrade head` before starting Uvicorn, automating schema migrations on every container startup.
- **Robust Health Check**: Updated `GET /health` to execute `SELECT 1` against RDS via SQLAlchemy, returning `{"status": "healthy", "database": "connected"}` on success and `503` if the database is unreachable.
- **Reusable Terraform Module**: `infra/terraform/modules/ec2/` with `main.tf`, `variables.tf`, and `outputs.tf`.

### Changed
- **`database.py`**: Added `pool_pre_ping=True`, `pool_size=5`, and `max_overflow=10` to the SQLAlchemy engine for resilient connection management in cloud environments.
- **`docker/Dockerfile`**: Updated `runner` stage to copy `infra/` (Alembic config + migrations) and `entrypoint.sh` as `ENTRYPOINT` with `exec` for correct signal handling.
- **`docker/entrypoint.sh`**: Invokes `alembic` and `uvicorn` directly from `/opt/venv/bin` — `uv` binary is not present in the `runner` stage.

### Infrastructure
- **Environment Updated**: `infra/terraform/envs/dev/main.tf` calls the `ec2` module consuming outputs from `networking` and `rds` modules.
- **New Outputs**: `ec2_instance_id` and `ec2_private_ip` exported from `envs/dev`.

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
