import typing

import fastapi
import modern_di
import modern_di_fastapi
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app import ioc
from app.application import build_app


@pytest.fixture(scope="session")
async def app() -> typing.AsyncIterator[fastapi.FastAPI]:
    app_ = build_app()
    async with LifespanManager(app_):
        yield app_


@pytest.fixture(scope="session")
async def client(app: fastapi.FastAPI) -> typing.AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(scope="session")
def di_container(app: fastapi.FastAPI) -> modern_di.Container:
    return modern_di_fastapi.fetch_di_container(app)


@pytest.fixture(scope="session")
async def db_connection(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncConnection]:
    engine = await ioc.Dependencies.database_engine.async_resolve(di_container)
    connection: typing.Final = await engine.connect()
    try:
        yield connection
    finally:
        await connection.close()
        await engine.dispose()


@pytest.fixture(autouse=True)
async def db_session(
    db_connection: AsyncConnection, di_container: modern_di.Container
) -> typing.AsyncIterator[AsyncSession]:
    transaction = await db_connection.begin()
    await db_connection.begin_nested()
    ioc.Dependencies.database_engine.override(db_connection, di_container)

    try:
        yield AsyncSession(db_connection, expire_on_commit=False, autoflush=False)
    finally:
        if db_connection.in_transaction():
            await transaction.rollback()
