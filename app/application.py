import contextlib
import typing

import fastapi
import modern_di_fastapi
from advanced_alchemy.exceptions import DuplicateKeyError
from lite_bootstrap import FastAPIBootstrapper, FastAPIConfig

from app import exceptions
from app.api.decks import ROUTER
from app.settings import settings


def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(ROUTER, prefix="/api")


class AppBuilder:
    def __init__(self) -> None:
        self.app: fastapi.FastAPI = fastapi.FastAPI(
            lifespan=self.lifespan_manager,
        )
        self.bootstrapper = FastAPIBootstrapper(
            bootstrap_config=FastAPIConfig(
                application=self.app,
                service_name=settings.service_name,
                service_version=settings.service_version,
                service_environment=settings.service_environment,
                service_debug=settings.service_debug,
                opentelemetry_endpoint=settings.opentelemetry_endpoint,
                sentry_dsn=settings.sentry_dsn,
                cors_allowed_origins=settings.cors_allowed_origins,
                cors_allowed_methods=settings.cors_allowed_methods,
                cors_allowed_headers=settings.cors_allowed_headers,
                cors_exposed_headers=settings.cors_exposed_headers,
                logging_buffer_capacity=settings.logging_buffer_capacity,
                swagger_offline_docs=settings.swagger_offline_docs,
            ),
        )
        self.bootstrapper.bootstrap()
        self.di_container = modern_di_fastapi.setup_di(self.app)
        include_routers(self.app)
        self.app.add_exception_handler(
            DuplicateKeyError,
            exceptions.duplicate_key_error_handler,  # type: ignore[arg-type]
        )

    @contextlib.asynccontextmanager
    async def lifespan_manager(self, _: fastapi.FastAPI) -> typing.AsyncIterator[dict[str, typing.Any]]:
        async with self.di_container:
            yield {}


application = AppBuilder().app
