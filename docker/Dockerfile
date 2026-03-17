# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Docker optimizations for uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy and install dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN mkdir -p apps/server/src
RUN uv sync --frozen --no-dev --no-install-project

# Install monorepo as a package
COPY . .
RUN uv sync --frozen --no-dev


# Stage 2: Runner
FROM python:3.12-slim AS runner
WORKDIR /app

# Create non-root user for Hardening
RUN adduser --disabled-password --gecos "" appuser

# Copy the virtual environment already prepared
COPY --from=builder /opt/venv /opt/venv

COPY . .

# SECURITY: The virtual environment belongs to root and is read-only for appuser
RUN chown -R root:root /opt/venv && \
    chmod -R 755 /opt/venv

# Activate the venv in the PATH
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1


USER appuser

EXPOSE 8000
CMD ["uvicorn", "apps.server.src.main:app", "--host", "0.0.0.0", "--port", "8000"]