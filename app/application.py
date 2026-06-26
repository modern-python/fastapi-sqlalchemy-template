import dataclasses
import typing

import modern_di
import modern_di_fastapi
from advanced_alchemy.exceptions import DuplicateKeyError, NotFoundError
from lite_bootstrap import FastAPIBootstrapper
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from app import exceptions, ioc
from app.api import cards, decks
from app.settings import settings


if typing.TYPE_CHECKING:
    import fastapi


def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(decks.ROUTER, prefix="/api")
    app.include_router(cards.ROUTER, prefix="/api")


def build_app() -> fastapi.FastAPI:
    di_container = modern_di.Container(groups=[ioc.Dependencies])
    bootstrap_config = dataclasses.replace(
        settings.api_bootstrapper_config,
        opentelemetry_instrumentors=[
            SQLAlchemyInstrumentor(),
            AsyncPGInstrumentor(capture_parameters=True),
        ],
    )
    bootstrapper = FastAPIBootstrapper(bootstrap_config=bootstrap_config)
    app: fastapi.FastAPI = bootstrapper.bootstrap()
    modern_di_fastapi.setup_di(app, di_container)
    include_routers(app)
    app.add_exception_handler(
        DuplicateKeyError,
        exceptions.duplicate_key_error_handler,  # ty: ignore[invalid-argument-type]
    )
    app.add_exception_handler(
        NotFoundError,
        exceptions.not_found_error_handler,  # ty: ignore[invalid-argument-type]
    )
    return app
