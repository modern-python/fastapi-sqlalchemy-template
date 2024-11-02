import contextlib
import typing

import fastapi
import modern_di
import modern_di_fastapi
from advanced_alchemy.exceptions import DuplicateKeyError, ForeignKeyError

from app import exceptions, ioc
from app.api.decks import ROUTER
from app.settings import settings


def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(ROUTER, prefix="/api")


class AppBuilder:
    def __init__(self) -> None:
        self.app: fastapi.FastAPI = fastapi.FastAPI(
            title=settings.service_name,
            debug=settings.debug,
            lifespan=self.lifespan_manager,
            dependencies=[fastapi.Depends(modern_di_fastapi.enter_di_request_scope)],
        )
        self.di_container = modern_di.Container(scope=modern_di.Scope.APP)
        modern_di_fastapi.save_di_container(self.app, self.di_container)
        include_routers(self.app)
        self.app.add_exception_handler(
            ForeignKeyError,
            exceptions.foreign_key_error_handler,  # type: ignore[arg-type]
        )
        self.app.add_exception_handler(
            DuplicateKeyError,
            exceptions.foreign_key_error_handler,  # type: ignore[arg-type]
        )

    @contextlib.asynccontextmanager
    async def lifespan_manager(self, _: fastapi.FastAPI) -> typing.AsyncIterator[dict[str, typing.Any]]:
        async with self.di_container:
            await ioc.IOCContainer.async_resolve_creators(self.di_container)
            yield {}


application = AppBuilder().app
