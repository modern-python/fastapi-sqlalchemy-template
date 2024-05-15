import granian
from granian.constants import Interfaces, Loops

from app import ioc


if __name__ == "__main__":
    settings = ioc.IOCContainer.settings.sync_resolve()
    granian.Granian(
        target="app.application:application",
        address="0.0.0.0",  # noqa: S104
        port=settings.app_port,
        interface=Interfaces.ASGI,
        log_dictconfig={"root": {"level": "INFO"}} if not settings.debug else {},
        log_level=settings.log_level,
        loop=Loops.uvloop,
    ).serve()
