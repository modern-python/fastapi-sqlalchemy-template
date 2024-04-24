from fastapi import FastAPI
from that_depends.providers import DIContextMiddleware

from app import exceptions
from app.api.decks import ROUTER
from app.exceptions import DatabaseValidationError
from app.settings import settings


def get_app() -> FastAPI:
    _app = FastAPI(
        title=settings.service_name,
        debug=settings.debug,
    )

    _app.include_router(ROUTER, prefix="/api")

    _app.add_middleware(DIContextMiddleware)

    _app.add_exception_handler(
        DatabaseValidationError,
        exceptions.database_validation_exception_handler,  # type: ignore[arg-type]
    )

    return _app


application = get_app()
