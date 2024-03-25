import runpy
from unittest import mock

import pytest

from app import __main__ as api_main
from app import ioc


async def test_init_resources() -> None:
    try:
        ioc.IOCContainer.reset_override()
        await ioc.IOCContainer.database_engine()
    finally:
        await ioc.IOCContainer.tear_down()


def test_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("granian.Granian", mock.Mock())
    runpy.run_module(api_main.__name__, run_name="__main__")
