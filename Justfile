default: install lint build test

# down all app containers
down:
    docker compose down --remove-orphans

# run shell in container
sh:
    docker compose run --service-ports application bash

# run pytest with arguments
test *args: down && down
    docker compose run application sh -c "sleep 1 && uv run alembic downgrade base && uv run alembic upgrade head && uv run pytest {{ args }}"

# run api
run:
    docker compose run --service-ports application sh -c "sleep 1 && uv run alembic upgrade head && uv run python -m app"

# create alembic migration with arguments
migration *args: && down
    docker compose run application sh -c "sleep 1 && uv run alembic upgrade head && uv run alembic revision --autogenerate {{ args }}"

# build app docker container
build:
    docker compose build application

# install local dependencies
install:
    uv lock --upgrade
    uv sync --all-extras --no-install-project --frozen

# run linters
lint:
    uv run ruff format .
    uv run ruff check . --fix
    uv run mypy .
