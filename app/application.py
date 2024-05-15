from fastapi import FastAPI
from that_depends.providers import DIContextMiddleware

from app import exceptions, ioc
from app.api.decks import ROUTER
from app.exceptions import DatabaseValidationError


def get_app() -> FastAPI:
    settings = ioc.IOCContainer.settings.sync_resolve()
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
