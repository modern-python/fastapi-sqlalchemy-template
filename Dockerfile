FROM python:3.14-slim

# required for psycopg2
RUN apt update \
    && apt install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN useradd --no-create-home --gid root runner

ENV UV_PROJECT_ENVIRONMENT=/code/.venv \
    UV_NO_MANAGED_PYTHON=1 \
    UV_NO_CACHE=true \
    UV_LINK_MODE=copy

WORKDIR /code

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --all-extras --frozen --no-install-project

COPY . .

RUN chown -R runner:root /code && chmod -R g=u /code

USER runner
