## Async template on FastAPI and SQLAlchemy 1.4

[![GitHub issues](https://img.shields.io/github/issues/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/issues)
[![GitHub forks](https://img.shields.io/github/forks/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/network)
[![GitHub stars](https://img.shields.io/github/stars/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/stargazers)
[![GitHub license](https://img.shields.io/github/license/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/blob/main/LICENSE)

### Description
Production-ready dockerized async REST API on FastAPI with SQLAlchemy and PostgreSQL

## Key Features
- tests on `pytest` with automatic rollback after each test case
- IOC (Inversion of Control) container built on [that-depends](https://github.com/modern-python/that-depends/) - my DI framework
- Linting and formatting using `ruff` and `mypy`
- `Alembic` for DB migrations

### After `git clone` run
```bash
task -l  # list of tasks with descriptions
```
