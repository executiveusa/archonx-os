FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    ; apt-get install -y --no-install-recommends git curl ca-certificates \
    ; rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml README.md archonx-config.json ./
COPY archonx ./archonx
COPY services ./services
COPY templates ./templates
COPY data ./data
COPY scripts ./scripts

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev

EXPOSE 8080

CMD ["uvicorn", "archonx.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
