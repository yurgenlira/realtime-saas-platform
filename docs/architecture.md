# Architecture Overview

## Design Patterns
- **Sidecar/Worker Pattern**: Decoupling ingestion from processing.
- **Shared Database (Logical Isolation)**: Column-based tenancy for simplicity and operational scale.

## Data Flow
1. API validates `X-API-KEY`.
2. Validated payload is buffered in Redis.
3. Worker asynchronously consumes and persists to PostgreSQL.
