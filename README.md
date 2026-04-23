# 🚀 Realtime SaaS Platform

Multi-tenant webhook ingestion platform designed using event-driven architecture and DevOps best practices.

## 🏗️ Architecture
```text
Client → FastAPI (Pydantic Validation) → SQS (ingestion-queue) → Worker (Long Polling) → PostgreSQL
```

### ☁️ Cloud Infrastructure (AWS)
```text
VPC (10.0.0.0/16)
  ├── Public Subnets  [us-east-1a, us-east-1b] → Internet Gateway → ALB (future)
  └── Private Subnets [us-east-1a, us-east-1b] → NAT Gateway
        ├── RDS PostgreSQL 16 Single-AZ ← rds_sg (port 5432 from app_sg only)
        │     DB Subnet Group · gp3 20GB encrypted · 7-day automated backups
        ├── EC2 t3.micro (API) + EC2 t3.micro (Worker) ← app_sg
        │     Docker: entrypoint → alembic upgrade head → uvicorn (API)
        │     Docker: entrypoint → python main.py (Worker)
        │     IAM Instance Profile (CloudWatch + SSM + ECR pull + Secrets Manager)
        │     Credentials: fetched from Secrets Manager at boot via Instance Profile
        └── SQS
              ├── ingestion-queue (Standard, retention: 4d, visibility_timeout: 30s)
              └── ingestion-dead-letter (retention: 14d, maxReceiveCount: 5)

ECR:
  ├── realtime-saas-api    (scan_on_push · lifecycle: last 10 images)
  └── realtime-saas-worker (scan_on_push · lifecycle: last 10 images)
Secrets Manager: realtime-saas/dev/rds (RDS credentials — KMS encrypted)
GitHub Actions Role (OIDC — no static credentials)
  ├── ecr:push → ECR repositories (api + worker)
  ├── ssm:SendCommand → EC2 instances
  └── terraform read → plan on PRs
GitHub Environments: dev, staging (variables scoped per deployment target)
Terraform workspaces: default (dev), staging
```

### ☁️ Production Target
```text
ALB → ECS Fargate (API/Worker) → SQS → RDS (PostgreSQL)
```

## 🛠️ Tech Stack
- **Runtime**: Python 3.12 (uv managed)
- **Framework**: FastAPI
- **Database**: PostgreSQL 16
- **Queue**: AWS SQS Standard (Long Polling, at-least-once, DLQ after 5 failures)
- **Secrets**: AWS Secrets Manager (RDS credentials)
- **Containerization**: Docker (Multi-stage, independent runner-api / runner-worker stages)
- **Orchestration**: Docker Compose / EC2 (cloud)
- **IaC**: Terraform 1.14.7 (AWS provider 6.40.0, remote state: S3 + DynamoDB, workspaces: dev/staging)
- **Quality**: Ruff, Pre-commit
- **Testing**: Pytest, pytest-cov (70% minimum coverage gate), LocalStack (SQS emulation for integration tests)
- **CI**: GitHub Actions (lint → unit tests → integration tests → docker build → terraform plan)
- **CD**: GitHub Actions (matrix build → push ECR api+worker → SSM RunCommand deploy, GitHub Environments)

## ⚡ Operational Quick Start

### 1. Provision Infrastructure

**Local (Docker):**
```bash
cp .env.example .env
make up
```

**Cloud (AWS — requires Terraform and valid AWS credentials):**
```bash
cd infra/terraform/envs/dev
export TF_VAR_db_password="your-secure-password"
export TF_VAR_github_token="your-github-token"
terraform init
terraform plan -out=tfplan
terraform apply tfplan
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
make test-unit          # unit tests — no containers required
make test-integration   # integration tests — requires make up (LocalStack)
make test               # full suite with coverage gate (70%)
```

## 📁 Project Organization
```text
.
├── apps/               # Scalable service containers (API, Worker)
├── libs/               # Shared domain logic & ORM models (domain package)
├── infra/
│   ├── migrations/     # Alembic schema versioning
│   └── terraform/      # AWS infrastructure as code
│       ├── modules/
│       │   ├── networking/       # VPC, subnets, IGW, NAT Gateway
│       │   ├── rds/              # RDS PostgreSQL, Security Groups, DB Subnet Group
│       │   ├── ec2/              # EC2 instance, IAM Instance Profile, user_data bootstrap
│       │   ├── ecr/              # ECR repository, lifecycle policy (api + worker)
│       │   ├── iam_github_oidc/  # OIDC Provider, GitHub Actions IAM Role
│       │   ├── sqs/              # SQS ingestion queue + Dead Letter Queue
│       │   └── secrets_manager/  # Secrets Manager secret for RDS credentials
│       └── envs/                 # Environment entry points (dev workspace, staging workspace)
├── docker/
│   ├── Dockerfile              # Multi-stage: builder · runner-api · runner-worker
│   └── localstack-init.sh      # SQS queue creation on LocalStack startup
└── Makefile            # Service orchestration interface
```

---
*Detailed documentation for security policies and CI/CD can be found in the [docs](./docs) directory.*

## 📝 Changelog

See [Changelog](CHANGELOG.md)