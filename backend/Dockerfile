FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
COPY pandasearch/ ./pandasearch/
RUN pip install -e ".[dev]"

# Run
CMD ["python", "-m", "pandasearch.main"]
