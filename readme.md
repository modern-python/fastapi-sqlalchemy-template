## Async template on FastAPI and SQLAlchemy 1.4

### Description
Production-ready dockerized async REST API on FastAPI with SQLAlchemy and PostgreSQL

## Key Features
- tests on `pytest` with automatic rollback after each test case
- db session stored in Python's `context variable`
- separate requirements files for dev and production using `pip-tools`
- configs for `mypy`, `pylint`, `isort` and `black`
- `Alembic` for DB migrations

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
