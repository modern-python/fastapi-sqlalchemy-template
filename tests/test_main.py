import runpy
from typing import TYPE_CHECKING
from unittest import mock

import modern_di
from sqlalchemy.ext.asyncio import AsyncSession

from app import ioc
from app.settings import settings


if TYPE_CHECKING:
    import pytest


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    granian = mock.Mock()
    monkeypatch.setattr("granian.Granian", granian)
    monkeypatch.setattr(settings, "app_workers", 4)

    runpy.run_module("app.__main__", run_name="__main__")

    assert granian.call_args.kwargs["workers"] == 4  # noqa: PLR2004
    assert "backpressure" not in granian.call_args.kwargs


async def test_session() -> None:
    container = modern_di.Container(groups=ioc.ALL_GROUPS)
    request_container = container.build_child_container(scope=modern_di.Scope.REQUEST)
    try:
        request_container.resolve(AsyncSession)
    finally:
        await request_container.close_async()
        await container.close_async()
