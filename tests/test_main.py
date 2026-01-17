import runpy
from typing import TYPE_CHECKING
from unittest import mock

import modern_di
from sqlalchemy.ext.asyncio import AsyncSession

from app import ioc


if TYPE_CHECKING:
    import pytest


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("granian.Granian", mock.Mock())
    runpy.run_module("app.__main__", run_name="__main__")


async def test_session() -> None:
    container = modern_di.Container(groups=[ioc.Dependencies])
    request_container = container.build_child_container(scope=modern_di.Scope.REQUEST)
    try:
        request_container.resolve(AsyncSession)
    finally:
        await request_container.close_async()
        await container.close_async()
