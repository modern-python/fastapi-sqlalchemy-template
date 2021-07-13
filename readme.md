## Async template on FastAPI and SQLAlchemy 1.4

[![GitHub issues](https://img.shields.io/github/issues/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/issues)
[![GitHub forks](https://img.shields.io/github/forks/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/network)
[![GitHub stars](https://img.shields.io/github/stars/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/stargazers)
[![GitHub license](https://img.shields.io/github/license/lesnik512/fast-api-sqlalchemy-template)](https://github.com/lesnik512/fast-api-sqlalchemy-template/blob/main/LICENSE)

### Description
Production-ready dockerized async REST API on FastAPI with SQLAlchemy and PostgreSQL

## Key Features
- tests on `pytest` with automatic rollback after each test case
- db session stored in Python's `context variable`
- separate requirements files for dev and production using `pip-tools`
- configs for `mypy`, `pylint`, `isort` and `black`
- `Alembic` for DB migrations
- Github CI

### After `git clone` run
```bash
make help
```

### Prepare virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install pip-tools
```
