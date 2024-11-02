## Async template on FastAPI and SQLAlchemy 2

[![Test Coverage](https://codecov.io/gh/modern-python/fastapi-sqlalchemy-template/branch/main/graph/badge.svg)](https://codecov.io/gh/modern-python/fastapi-sqlalchemy-template)
[![GitHub issues](https://img.shields.io/github/issues/modern-python/fastapi-sqlalchemy-template)](https://github.com/modern-python/fastapi-sqlalchemy-template/issues)
[![GitHub forks](https://img.shields.io/github/forks/modern-python/fastapi-sqlalchemy-template)](https://github.com/modern-python/fastapi-sqlalchemy-template/network)
[![GitHub stars](https://img.shields.io/github/stars/modern-python/fastapi-sqlalchemy-template)](https://github.com/modern-python/fastapi-sqlalchemy-template/stargazers)

### Description
Production-ready dockerized async REST API on FastAPI with SQLAlchemy and PostgreSQL

## Key Features
- tests on `pytest` with automatic rollback after each test case
- IOC (Inversion of Control) container built on [modern-di](https://github.com/modern-python/modern-di/) - my DI framework
- Linting and formatting using `ruff` and `mypy`
- `Alembic` for DB migrations

### After `git clone` run
```bash
just --list
```
