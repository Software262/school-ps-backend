FROM ghcr.io/astral-sh/uv:python3.13-alpine AS base

# Common environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONOPTIMIZE=2 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

# Stage 1: Builder
FROM base AS builder

# Install build dependencies in a single layer
RUN apk add --no-cache --virtual .build-deps \
  build-base \
  gcc \
  musl-dev \
  libffi-dev

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies and clean up in a single layer
RUN mkdir -p .venv && \
  uv sync --frozen --no-dev --no-cache && \
  find /app/.venv -name "*.pyc" -delete && \
  find /app/.venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
  find /app/.venv -name "*.pyo" -delete && \
  find /app/.venv -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
  find /app/.venv -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
  apk del .build-deps

# Stage 2: Runtime
FROM base AS runtime

# Install only necessary runtime dependencies
RUN apk add --no-cache \
  libgcc \
  libstdc++ \
  libffi \
  && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S appgroup \
  && adduser -u 1001 -S appuser -G appgroup -h /app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Set PATH for the virtual environment and additional variables
ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH" \
  WORKERS=1 \
  PORT=8080 \
  LOG_LEVEL=info

# Copy application code
COPY --chown=appuser:appgroup app/ app/

# Switch to non-root user
USER appuser

# Expose dynamic port
EXPOSE $PORT

# Default command optimized with environment variables in JSON format
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers $WORKERS --log-level $LOG_LEVEL"]
