import runpy
from unittest import mock

import fastapi
import modern_di
import pytest

from app import __main__ as api_main
from app import ioc
from app.application import AppBuilder


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("granian.Granian", mock.Mock())
    runpy.run_module(api_main.__name__, run_name="__main__")


async def test_app_lifespan() -> None:
    async with AppBuilder().lifespan_manager(fastapi.FastAPI()):
        pass


async def test_session() -> None:
    async with (
        modern_di.Container(scope=modern_di.Scope.APP) as container,
        container.build_child_container(scope=modern_di.Scope.REQUEST) as request_container,
    ):
        await ioc.Dependencies.session.async_resolve(request_container)
