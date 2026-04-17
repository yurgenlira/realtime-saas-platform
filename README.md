# 🚀 Realtime SaaS Platform

Multi-tenant webhook ingestion platform designed using event-driven architecture and DevOps best practices.

## 🏗️ Architecture
```text
Client → FastAPI (Pydantic Validation) → Redis (In-memory Queue) → Worker (Background Tasks) → PostgreSQL
```

### ☁️ Cloud Infrastructure (AWS)
```text
VPC (10.0.0.0/16)
  ├── Public Subnets  [us-east-1a, us-east-1b] → Internet Gateway → ALB (future)
  └── Private Subnets [us-east-1a, us-east-1b] → NAT Gateway
        ├── RDS PostgreSQL 16 Single-AZ ← rds_sg (port 5432 from app_sg only)
        │     DB Subnet Group · gp3 20GB encrypted · 7-day automated backups
        └── EC2 t3.micro (API + Worker) ← app_sg
              Docker: entrypoint → alembic upgrade head → uvicorn
              IAM Instance Profile (CloudWatch + SSM + ECR pull)

ECR: realtime-saas-api  (scan_on_push · lifecycle: last 10 images)
GitHub Actions Role (OIDC — no static credentials)
  ├── ecr:push → ECR repository
  ├── ssm:SendCommand → EC2 instance
  └── terraform read → plan on PRs
```

### ☁️ Production Target
```text
ALB → ECS Fargate (API/Worker) → ElastiCache (Redis) → RDS (PostgreSQL)
```

## 🛠️ Tech Stack
- **Runtime**: Python 3.12 (uv managed)
- **Framework**: FastAPI
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Containerization**: Docker (Multi-stage, Non-root, Alembic entrypoint)
- **Orchestration**: Docker Compose / EC2 (cloud)
- **IaC**: Terraform 1.14.7 (AWS provider 6.40.0, remote state: S3 + DynamoDB)
- **Quality**: Ruff, Pre-commit
- **Testing**: Pytest, pytest-cov (70% minimum coverage gate)
- **CI**: GitHub Actions (lint → test → docker build → terraform plan)
- **CD**: GitHub Actions (build → push ECR → SSM RunCommand deploy)

## ⚡ Operational Quick Start

### 1. Provision Infrastructure

**Local (Docker):**
```bash
make up
```

**Cloud (AWS — requires Terraform and valid AWS credentials):**
```bash
cd infra/terraform/envs/dev
export TF_VAR_db_password="your-secure-password"
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
cd apps/api && uv run pytest tests/unit/ -v
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
│       │   ├── ecr/              # ECR repository, lifecycle policy
│       │   └── iam_github_oidc/  # OIDC Provider, GitHub Actions IAM Role
│       └── envs/                 # Environment entry points (dev, staging, prod)
├── docker/             # Hardened container definitions
└── Makefile            # Service orchestration interface
```

---
*Detailed documentation for security policies and CI/CD can be found in the [docs](./docs) directory.*

## 📝 Changelog

See [Changelog](CHANGELOG.md)