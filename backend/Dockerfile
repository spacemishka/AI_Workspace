# =============================================================================
# Backend Dockerfile (Multi-stage build)
# =============================================================================

FROM python:3.12-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Development Stage ─────────────────────────────────────────────────────────
FROM base AS development

COPY pyproject.toml README.md ./
RUN pip install hatchling && pip install -e ".[dev]"

COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production Stage ──────────────────────────────────────────────────────────
FROM base AS production

COPY pyproject.toml README.md ./
RUN pip install hatchling && pip install .

COPY ./src ./src

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
