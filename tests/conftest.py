import typing

import modern_di_fastapi
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import event

from app import ioc
from app.application import build_app
from app.resources.db import create_primary_sa_engine, create_session


if typing.TYPE_CHECKING:
    import fastapi
    import modern_di
    from sqlalchemy.engine import Connection
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession


SAVEPOINT_PREFIXES: typing.Final = ("SAVEPOINT", "RELEASE SAVEPOINT", "ROLLBACK TO SAVEPOINT")


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
    engine = create_primary_sa_engine()
    connection = await engine.connect()
    transaction = await connection.begin()
    di_container.override(ioc.Database.dynamic_engine, connection)
    # Switching the shared connection to AUTOCOMMIT would roll back the outer transaction.
    di_container.override(ioc.Database.autocommit_isolation_level, None)

    try:
        yield create_session(connection)
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


@pytest.fixture
def statements(db_session: AsyncSession) -> typing.Iterator[list[str]]:
    sync_connection: typing.Final = typing.cast("Connection", db_session.sync_session.bind)
    recorded: typing.Final[list[str]] = []

    def record(*args: object) -> None:
        statement: typing.Final = typing.cast("str", args[2])
        if not statement.startswith(SAVEPOINT_PREFIXES):
            recorded.append(statement)

    event.listen(sync_connection, "before_cursor_execute", record)
    try:
        yield recorded
    finally:
        event.remove(sync_connection, "before_cursor_execute", record)


@pytest.fixture
async def committing_engine(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncEngine]:
    engine = create_primary_sa_engine()
    di_container.override(ioc.Database.dynamic_engine, engine)
    try:
        yield engine
    finally:
        di_container.reset_override(ioc.Database.dynamic_engine)
        await engine.dispose()
