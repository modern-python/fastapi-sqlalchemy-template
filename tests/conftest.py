import typing

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import ioc
from app.application import application


@pytest.fixture()
async def client() -> typing.AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=application),  # type: ignore[arg-type]
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(autouse=True)
async def _prepare_ioc_container() -> typing.AsyncIterator[None]:
    engine = await ioc.IOCContainer.database_engine()
    connection = await engine.connect()
    transaction = await connection.begin()
    await connection.begin_nested()
    session = AsyncSession(connection, expire_on_commit=False, autoflush=False)
    ioc.IOCContainer.session.override(session)

    try:
        yield
    finally:
        if connection.in_transaction():
            await transaction.rollback()
        await connection.close()

        ioc.IOCContainer.reset_override()
        await ioc.IOCContainer.tear_down()
