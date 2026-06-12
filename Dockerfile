FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONOPTIMIZE=2 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

# Stage 1: Builder
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  gcc \
  libffi-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN mkdir -p .venv && \
  uv sync --frozen --no-dev --group prod --no-cache && \
  find /app/.venv -name "*.pyc" -delete && \
  find /app/.venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; \
  find /app/.venv -name "*.pyo" -delete && \
  find /app/.venv -type d -name "tests" -exec rm -rf {} + 2>/dev/null; \
  find /app/.venv -type d -name "test" -exec rm -rf {} + 2>/dev/null; \
  true

# Stage 2: Runtime
FROM base AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
  libffi8 \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1001 appgroup \
  && useradd -u 1001 -g appgroup -m -d /app appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

ENV VIRTUAL_ENV=/app/.venv \
  PATH="/app/.venv/bin:$PATH" \
  WORKERS=1 \
  PORT=8080 \
  LOG_LEVEL=info

COPY --chown=appuser:appgroup app/ app/

USER appuser

EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers $WORKERS --log-level $LOG_LEVEL"]
