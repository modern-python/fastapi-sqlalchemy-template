import runpy
from typing import TYPE_CHECKING
from unittest import mock

import modern_di

from app import ioc


if TYPE_CHECKING:
    import pytest


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("granian.Granian", mock.Mock())
    runpy.run_module("app.__main__", run_name="__main__")


async def test_session() -> None:
    async with (
        modern_di.AsyncContainer() as container,
        container.build_child_container(scope=modern_di.Scope.REQUEST) as request_container,
    ):
        await request_container.resolve_provider(ioc.Dependencies.session)
