FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for compiling Python C extensions
# (asyncpg, uvicorn[standard], pgvector, torch, etc. need gcc and libpq-dev)
# Use --fix-missing to handle transient network failures
RUN set -ex; \
    apt-get update --fix-missing; \
    apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY backend/pyproject.toml ./
COPY backend/pandasearch/ ./pandasearch/
COPY models/ /models/

# Install Python dependencies (production only, no dev tools)
RUN pip install --no-cache-dir -e "."

# Run
CMD ["python", "-m", "pandasearch.main"]
