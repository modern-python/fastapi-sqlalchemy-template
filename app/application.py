import dataclasses

import fastapi
import modern_di_fastapi
from advanced_alchemy.exceptions import DuplicateKeyError
from lite_bootstrap import FastAPIBootstrapper
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from app import exceptions
from app.api.decks import ROUTER
from app.settings import settings


def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(ROUTER, prefix="/api")


def build_app() -> fastapi.FastAPI:
    bootstrap_config = dataclasses.replace(
        settings.api_bootstrapper_config,
        opentelemetry_instrumentors=[
            SQLAlchemyInstrumentor(),
            AsyncPGInstrumentor(capture_parameters=True),  # type: ignore[no-untyped-call]
        ],
    )
    bootstrapper = FastAPIBootstrapper(bootstrap_config=bootstrap_config)
    app: fastapi.FastAPI = bootstrapper.bootstrap()
    modern_di_fastapi.setup_di(app)
    include_routers(app)
    app.add_exception_handler(
        DuplicateKeyError,
        exceptions.duplicate_key_error_handler,  # type: ignore[arg-type]
    )
    return app
