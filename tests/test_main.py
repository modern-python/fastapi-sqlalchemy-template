import runpy
from unittest import mock

import modern_di
import pytest

from app import ioc


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("granian.Granian", mock.Mock())
    runpy.run_module("app.__main__", run_name="__main__")


async def test_session() -> None:
    async with (
        modern_di.Container(scope=modern_di.Scope.APP) as container,
        container.build_child_container(scope=modern_di.Scope.REQUEST) as request_container,
    ):
        await ioc.Dependencies.session.async_resolve(request_container)
