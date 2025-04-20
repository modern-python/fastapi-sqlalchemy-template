import granian
from granian.constants import Interfaces, Loops
from granian.log import LogLevels

from app.settings import settings


if __name__ == "__main__":
    granian.Granian(  # type: ignore[attr-defined]
        target="app.application:application",
        address="0.0.0.0",  # noqa: S104
        port=settings.app_port,
        interface=Interfaces.ASGI,
        log_level=LogLevels(settings.log_level),
        loop=Loops.uvloop,
    ).serve()
