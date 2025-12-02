import typing

import modern_di_fastapi
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import ioc
from app.application import build_app


if typing.TYPE_CHECKING:
    import fastapi
    import modern_di


@pytest.fixture
async def app() -> typing.AsyncIterator[fastapi.FastAPI]:
    app_ = build_app()
    async with LifespanManager(app_):
        yield app_


@pytest.fixture
async def client(app: fastapi.FastAPI) -> typing.AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def di_container(app: fastapi.FastAPI) -> modern_di.AsyncContainer:
    return modern_di_fastapi.fetch_di_container(app)


@pytest.fixture(autouse=True)
async def db_session(di_container: modern_di.AsyncContainer) -> typing.AsyncIterator[AsyncSession]:
    engine = await di_container.resolve_provider(ioc.Dependencies.database_engine)
    connection = await engine.connect()
    transaction = await connection.begin()
    await connection.begin_nested()
    di_container.override(ioc.Dependencies.database_engine, connection)

    try:
        yield AsyncSession(connection, expire_on_commit=False, autoflush=False)
    finally:
        if connection.in_transaction():
            await transaction.rollback()
        await connection.close()
        await engine.dispose()
