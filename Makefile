## ---------------------------------------------------------------
## Quest Manager
## ---------------------------------------------------------------
## Local environment commands:
## ---------------------------------------------------------------

## up:        start app in docker
up: down
	docker-compose up

## pytest:    run pytest (with down/up migrations before)
pytest:
	docker-compose run app ./docker-entrypoint.sh pytest

## tests:     run isort, black, pylint, mypy, pytest
tests:
	docker-compose run app ./docker-entrypoint.sh tests

## migration: create alembic migration
migration: down
	docker-compose run app ./docker-entrypoint.sh migration 8000 $(ARGS)

down:
	docker-compose down --remove-orphans

build:
	docker-compose build

## ---------------------------------------------------------------
## Requirements managing: pip-tools required to be installed and
## pip-compile command required to be available
## ---------------------------------------------------------------

## pip-compile: compile all requirements
# https://github.com/jazzband/pip-tools/issues/1092#issuecomment-632584777
pip-compile: prepare-constraints
	pip-compile constraints.in
	pip-compile requirements.prod.in
	pip-compile requirements.dev.in

## pip-upgrade: upgrade all requirements
pip-upgrade: prepare-constraints
	pip-compile constraints.in --upgrade
	rm -f requirements.prod.txt requirements.dev.txt
	pip-compile requirements.prod.in
	pip-compile requirements.dev.in

prepare-constraints: check-pip-compile
	rm -f constraints.in
	touch constraints.txt
	cat requirements.*.in > constraints.in

## pip-sync:    sync requirements in local environment
pip-sync: check-pip-compile
	pip-sync requirements.prod.txt requirements.dev.txt

check-pip-compile:
	@which pip-compile > /dev/null

help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)
