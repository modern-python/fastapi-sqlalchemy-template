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
    uv run ty check

adr_check_source := "https://raw.githubusercontent.com/modern-python/.github/main/tests/test_adr_citations.py"

# Tracks main on purpose: the shared check is unpinned.
adr-check:
    #!/usr/bin/env sh
    set -eu
    dir="$(mktemp -d .adr-check.XXXXXX)"
    trap 'rm -rf "$dir"' EXIT
    curl -fsSL "{{ adr_check_source }}" -o "$dir/test_adr_citations.py"
    uv run --no-sync pytest --rootdir=. --noconftest -o addopts= "$dir/test_adr_citations.py"
