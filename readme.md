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

### Description
Production-ready dockerized async REST API on FastAPI with SQLAlchemy and PostgreSQL

## Key Features
- tests on `pytest` with automatic rollback after each test case
- IOC (Inversion of Control) container built on [modern-di](https://github.com/modern-python/modern-di/)
- Observability tools integration built on [lite-bootstrap](https://github.com/modern-python/lite-bootstrap/)
- Linting and formatting using `ruff` and `ty`
- `Alembic` for DB migrations

You can clone this project or use [this template](https://github.com/modern-python/modern-python-template) for fast [micro]service creation from scratch.

### After `git clone` run
```bash
just --list
```

## 📝 [License](LICENSE)

## Part of `modern-python`

Browse the full list of templates and libraries in
[`modern-python`](https://github.com/modern-python) — see the org profile for the categorized index.
