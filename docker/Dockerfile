# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app
COPY apps/server/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3.12-slim AS runner
WORKDIR /app

# Create non-root user for Hardening
RUN adduser --disabled-password --gecos "" appuser

# Copy only what's needed from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY apps/server/src ./src

# Adjust PATH and permissions
ENV PATH=/home/appuser/.local/bin:$PATH
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]