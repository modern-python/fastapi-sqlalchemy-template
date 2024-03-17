from fastapi import Depends, FastAPI

from app import exceptions
from app.apps.decks.views import router as decks_router
from app.db.deps import set_db
from app.db.exceptions import DatabaseValidationError
from app.settings import settings


def get_app() -> FastAPI:
    _app = FastAPI(
        title=settings.service_name,
        debug=settings.debug,
        dependencies=[Depends(set_db)],
    )

    _app.include_router(decks_router, prefix="/api")

    _app.add_exception_handler(
        DatabaseValidationError,
        exceptions.database_validation_exception_handler,  # type: ignore[arg-type]
    )

    return _app


application = get_app()
