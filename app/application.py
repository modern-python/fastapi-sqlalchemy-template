import dataclasses
from typing import TYPE_CHECKING

import modern_di
import modern_di_fastapi
from advanced_alchemy.exceptions import DuplicateKeyError
from lite_bootstrap import FastAPIBootstrapper
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from app import exceptions, ioc
from app.api.decks import ROUTER
from app.settings import settings


if TYPE_CHECKING:
    import fastapi


def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(ROUTER, prefix="/api")


def build_app() -> fastapi.FastAPI:
    di_container = modern_di.AsyncContainer(groups=[ioc.Dependencies])
    bootstrap_config = dataclasses.replace(
        settings.api_bootstrapper_config,
        opentelemetry_instrumentors=[
            SQLAlchemyInstrumentor(),
            AsyncPGInstrumentor(capture_parameters=True),  # type: ignore[no-untyped-call]
        ],
    )
    bootstrapper = FastAPIBootstrapper(bootstrap_config=bootstrap_config)
    app: fastapi.FastAPI = bootstrapper.bootstrap()
    modern_di_fastapi.setup_di(app, di_container)
    include_routers(app)
    app.add_exception_handler(
        DuplicateKeyError,
        exceptions.duplicate_key_error_handler,  # type: ignore[arg-type]
    )
    return app
