# ==========================================
# Stage 1: Base
# ==========================================
FROM python:3.12-slim AS base
WORKDIR /app

# Enable bytecode compilation, copy mode, and specify venv location
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv


# ==========================================
# Stage 2: Builder
# ==========================================
FROM base AS builder

# Copy manifests first to cache dependency layer
COPY pyproject.toml uv.lock ./
COPY apps/api/pyproject.toml ./apps/api/
COPY apps/worker/pyproject.toml ./apps/worker/
COPY libs/domain/pyproject.toml ./libs/domain/

# Create dummy source files so hatchling can build api and domain before COPY . .
RUN mkdir -p apps/api/src/api libs/domain/src/domain && \
    touch apps/api/src/api/__init__.py libs/domain/src/domain/__init__.py

# Install external dependencies, skipping the workspace packages
RUN uv sync --frozen --no-dev --no-install-project --all-packages

# Copy source code
COPY . .

# Install workspace members into the environment packages (Non-editable for prod)
RUN uv sync --frozen --no-dev --no-editable --all-packages


# ==========================================
# Stage 3: Dev
# ==========================================
FROM base AS dev

# Uses the builder environment but installs dev dependencies and uses editable mode
COPY --from=builder /opt/venv /opt/venv
COPY . .
RUN uv sync --all-packages

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ==========================================
# Stage 4: Runner API (prod)
# ==========================================
FROM python:3.12-slim AS runner-api
WORKDIR /app

# Non-root user
RUN adduser --disabled-password --gecos "" appuser

# Copy the pre-built virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy Alembic config and migration scripts
COPY infra/ /app/infra/

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# ==========================================
# Stage 5: Runner Worker (prod)
# ==========================================
FROM python:3.12-slim AS runner-worker
WORKDIR /app

# Non-root user
RUN adduser --disabled-password --gecos "" appuser

# Copy the pre-built virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Copy worker code
COPY apps/worker/main.py /app/apps/worker/main.py

USER appuser

ENTRYPOINT ["python", "/app/apps/worker/main.py"]