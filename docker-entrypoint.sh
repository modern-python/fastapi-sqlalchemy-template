#!/bin/bash
set -e

PORT=${2:-8000}

case "$1" in
    init)
        alembic upgrade head
        ;;
    api)
        exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
        ;;
    start)
        alembic upgrade head
        uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload
        ;;
    migration)
        alembic revision --autogenerate -m "$3"
        ;;
    tests)
        isort -c --diff --settings-file .isort.cfg .
        black --config pyproject.toml --check .
        pylint --rcfile=.pylintrc --errors-only app
        mypy .
        alembic downgrade base
        alembic upgrade head
        pytest -s -vv tests/
        ;;
    pytest)
        alembic downgrade base
        alembic upgrade head
        pytest -s -vv -x tests/
        ;;
    *)
        exec "$@"
        ;;
esac
