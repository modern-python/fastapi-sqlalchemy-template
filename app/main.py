from fastapi import FastAPI

from app import exceptions
from app.api.views import router
from app.config import settings
from app.db import DatabaseValidationError


def get_app() -> FastAPI:
    _app = FastAPI(title=settings.SERVICE_NAME, debug=settings.DEBUG)

    _app.include_router(router, prefix="/api")

    _app.add_exception_handler(
        DatabaseValidationError,
        exceptions.database_validation_exception_handler,
    )

    return _app


app = get_app()
