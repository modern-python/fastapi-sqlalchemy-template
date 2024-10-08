import contextlib
import typing

import fastapi
from advanced_alchemy.exceptions import ForeignKeyError

from app import exceptions, ioc
from app.api.decks import ROUTER


def include_routers(app: fastapi.FastAPI) -> None:
    app.include_router(ROUTER, prefix="/api")


class AppBuilder:
    def __init__(self) -> None:
        self.settings = ioc.IOCContainer.settings.sync_resolve()
        self.app: fastapi.FastAPI = fastapi.FastAPI(
            title=self.settings.service_name,
            debug=self.settings.debug,
            lifespan=self.lifespan_manager,
        )
        include_routers(self.app)
        self.app.add_exception_handler(
            ForeignKeyError,
            exceptions.foreign_key_error_handler,  # type: ignore[arg-type]
        )

    @contextlib.asynccontextmanager
    async def lifespan_manager(self, _: fastapi.FastAPI) -> typing.AsyncIterator[dict[str, typing.Any]]:
        try:
            await ioc.IOCContainer.init_resources()
            yield {}
        finally:
            await ioc.IOCContainer.tear_down()


application = AppBuilder().app
