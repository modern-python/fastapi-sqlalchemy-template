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
- configs for `mypy`, `pylint`, `isort` and `black`
- `Alembic` for DB migrations
- CI with Github

### After `git clone` run
```bash
task -l  # list of tasks with descriptions
```

### Prepare virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
poetry install
```

# [Poetry](https://python-poetry.org/docs/)

Poetry is python package manager.

Poetry resolve dependencies and conflicts in package and make it fast.

## Basic usage

- `poetry lock` lock dependencies
- `poetry update` lock, update and install dependencies
- `poetry install` for install dependencies from pyproject.toml
- `poetry add <package>` for adding dependency with check on conflicts
- `poetry remove <package>` for remove
- `poetry self update` update poetry

# [Task](https://taskfile.dev/)

Task is a task runner / build tool that aims to be simpler and easier to use than, for example, GNU Make.

## Basic usage

- `task -l` - list of tasks with descriptions
- `task -a` - list of all tasks
