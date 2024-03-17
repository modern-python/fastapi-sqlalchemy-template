ARG ENVIRONMENT="prod"
FROM python:3.12-slim

# required for psycopg2
RUN apt update \
    && apt install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip poetry
RUN useradd --no-create-home --gid root runner

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /code

COPY pyproject.toml .
COPY poetry.lock .

RUN [ "$ENVIRONMENT" = "prod" ] && poetry install --no-dev || poetry install

COPY . .

RUN chown -R runner:root /code && chmod -R g=u /code

USER runner
