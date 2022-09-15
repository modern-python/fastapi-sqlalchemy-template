ARG ENVIRONMENT="prod"
FROM python:3.10-slim

RUN apt update \
    && apt upgrade -y \
    && apt install -y curl \
        locales \
    && rm -rf /var/lib/apt/lists/*
# RU Locale
RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen
RUN pip3 install --no-cache-dir --upgrade pip \
    poetry
RUN useradd --no-create-home --gid root runner

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /code

COPY pyproject.toml .
COPY poetry.lock .

RUN [ "$ENVIRONMENT" = "prod" ] && poetry install --no-dev || poetry install

COPY . .

RUN chown -R runner:root /code \
    && chmod -R g=u /code

USER runner

EXPOSE 8000

ENTRYPOINT [ "/code/docker-entrypoint.sh" ]
