<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)"  srcset="https://raw.githubusercontent.com/modern-python/.github/main/brand/projects/fastapi-sqlalchemy-template/lockup-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/modern-python/.github/main/brand/projects/fastapi-sqlalchemy-template/lockup-light.svg">
    <img alt="fastapi-sqlalchemy-template" src="https://raw.githubusercontent.com/modern-python/.github/main/brand/projects/fastapi-sqlalchemy-template/lockup.png" width="420">
  </picture>
</p>

[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/modern-python/fastapi-sqlalchemy-template/actions/workflows/main.yml)
[![CI](https://github.com/modern-python/fastapi-sqlalchemy-template/actions/workflows/main.yml/badge.svg)](https://github.com/modern-python/fastapi-sqlalchemy-template/actions/workflows/main.yml)
[![License](https://img.shields.io/github/license/modern-python/fastapi-sqlalchemy-template.svg)](https://github.com/modern-python/fastapi-sqlalchemy-template/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/modern-python/fastapi-sqlalchemy-template)](https://github.com/modern-python/fastapi-sqlalchemy-template/stargazers)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)

## Description
Dockerized FastAPI, SQLAlchemy 2 and PostgreSQL app template with DI.

## Key features
- tests on `pytest` with automatic rollback after each test case
- IOC (Inversion of Control) container built on [modern-di](https://github.com/modern-python/modern-di/)
- Observability tools integration built on [lite-bootstrap](https://github.com/modern-python/lite-bootstrap/)
- Linting and formatting with `ruff`, type checking with `ty`
- `Alembic` for DB migrations

Authentication is intentionally omitted: pick the scheme that fits your project and add it as a FastAPI dependency.

## After `git clone` run
```bash
just --list
```

## Tracing in production
Setting `OPENTELEMETRY_ENDPOINT` turns tracing on, and by default every request is traced. In a benchmark of `GET /api/decks/{id}/`, that cut throughput by about 40%. Sampling with the standard OpenTelemetry variables brings that down to about 20%:

```bash
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1
```

This keeps one trace in ten, and follows the caller's decision when a request arrives with a trace context. Errors still reach Sentry when `SENTRY_DSN` is set.

The template also turns off the ASGI `send` and `receive` spans (`opentelemetry_exclude_spans` in `app/settings.py`), so each request records its server span and database spans only. With every request traced, that raised throughput by 5 to 8% in the same benchmark. Remove the setting if you need those spans.

## 📝 [License](https://github.com/modern-python/fastapi-sqlalchemy-template/blob/main/LICENSE)

## Part of `modern-python`

Browse the full list of templates and libraries in
[`modern-python`](https://github.com/modern-python); the org profile has the categorized index.
