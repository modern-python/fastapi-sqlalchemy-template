default: install lint build test

down:
    docker compose down --remove-orphans

sh:
    docker compose run --service-ports application bash

test *args: down && down
    docker compose run application sh -c "sleep 1 && uv run alembic downgrade base && uv run alembic upgrade head && uv run pytest {{ args }}"

run:
    docker compose run --service-ports application sh -c "sleep 1 && uv run alembic upgrade head && uv run python -m app"

migration *args: && down
    docker compose run application sh -c "sleep 1 && uv run alembic upgrade head && uv run alembic revision --autogenerate {{ args }}"

build:
    docker compose build application

install:
    uv lock --upgrade
    uv sync --all-extras --all-groups --no-install-project --frozen

lint:
    uv run eof-fixer .
    uv run ruff format .
    uv run ruff check . --fix
    uv run mypy .
