#!/bin/bash
set -e

WORKERS=${2:-5}

case "$1" in
    init)
        alembic upgrade head
        ;;
    api)
        exec uvicorn app.main:app --workers $WORKERS --host 0.0.0.0
        ;;
    start)
        alembic upgrade head
        uvicorn app.main:app --workers $WORKERS --host 0.0.0.0 --reload
        ;;
    migrate)
        alembic revision --autogenerate -m "$3"
        ;;
    tests)
        isort -c --diff --settings-file .isort.cfg .
        black --config pyproject.toml --check .
        pylint --rcfile=.pylintrc --errors-only app
        pytest -s -vv tests/
        ;;
    pytest)
        pytest -s -vv -x tests/
        ;;
    *)
        exec "$@"
        ;;
esac
