import typing

import modern_di_fastapi
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.application import build_app
from app.resources.db import create_sa_engine


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
async def di_container(app: fastapi.FastAPI) -> typing.AsyncIterator[modern_di.Container]:
    container = modern_di_fastapi.fetch_di_container(app)
    try:
        yield container
    finally:
        await container.close_async()


@pytest.fixture
async def db_session(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncSession]:
    engine = create_sa_engine()
    connection = await engine.connect()
    transaction = await connection.begin()
    await connection.begin_nested()
    di_container.override(dependency_type=AsyncEngine, mock=connection)

    try:
        yield AsyncSession(connection, expire_on_commit=False, autoflush=False)
    finally:
        if connection.in_transaction():
            await transaction.rollback()
        await connection.close()
        await engine.dispose()
        di_container.reset_override()


@pytest.fixture
async def set_async_session_in_base_sqlalchemy_factory(
    db_session: AsyncSession,
) -> typing.AsyncIterator[None]:
    try:
        SQLAlchemyFactory.__async_session__ = db_session
        yield
    finally:
        SQLAlchemyFactory.__async_session__ = None
