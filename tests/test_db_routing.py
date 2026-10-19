import typing

import fastapi
import modern_di
import pytest
import sqlalchemy as sa
from modern_di import Scope
from sqlalchemy.exc import DBAPIError

from app import ioc, models
from app.resources.db import create_sa_engine, read_engine_url
from app.settings import Settings, settings


if typing.TYPE_CHECKING:
    from sqlalchemy.engine.url import URL
    from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.fixture
async def primary_engine(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncEngine]:
    engine = create_sa_engine(settings=settings, url=settings.db_dsn_parsed)
    di_container.override(ioc.Database.database_engine, engine)
    yield engine
    await engine.dispose()


@pytest.fixture
async def read_engine(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncEngine]:
    engine = create_sa_engine(settings=settings, url=read_engine_url(settings), read_only=True)
    di_container.override(ioc.Database.database_read_engine, engine)
    yield engine
    await engine.dispose()


def resolve_engine(di_container: modern_di.Container, method: str | None) -> AsyncEngine:
    context = {fastapi.Request: fastapi.Request({"type": "http", "method": method})} if method else None
    with di_container.build_child_container(scope=Scope.REQUEST, context=context) as request_container:
        return request_container.resolve_provider(ioc.Database.dynamic_engine)


@pytest.mark.parametrize("method", ["GET", "HEAD"])
def test_safe_methods_use_read_engine(
    di_container: modern_di.Container, primary_engine: AsyncEngine, read_engine: AsyncEngine, method: str
) -> None:
    engine = resolve_engine(di_container, method)
    assert engine is read_engine
    assert engine is not primary_engine


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_write_methods_use_primary(
    di_container: modern_di.Container, primary_engine: AsyncEngine, read_engine: AsyncEngine, method: str
) -> None:
    engine = resolve_engine(di_container, method)
    assert engine is primary_engine
    assert engine is not read_engine


@pytest.mark.usefixtures("read_engine")
def test_no_request_uses_primary(di_container: modern_di.Container, primary_engine: AsyncEngine) -> None:
    assert resolve_engine(di_container, None) is primary_engine


async def resolve_read_engine_url(app_settings: Settings) -> URL:
    container: typing.Final = modern_di.Container(groups=ioc.ALL_GROUPS)
    container.override(ioc.Config.settings, app_settings)
    try:
        return container.resolve_provider(ioc.Database.database_read_engine).url
    finally:
        await container.close_async()


async def test_read_engine_built_from_primary_dsn_without_replica() -> None:
    assert await resolve_read_engine_url(Settings(db_replica_dsn="")) == settings.db_dsn_parsed


async def test_read_engine_built_from_overridden_replica_dsn() -> None:
    replica_settings: typing.Final = Settings(db_replica_dsn="postgresql+asyncpg://postgres:password@replica/postgres")
    assert (await resolve_read_engine_url(replica_settings)).host == "replica"


async def test_read_engine_runs_each_statement_in_its_own_transaction() -> None:
    engine = create_sa_engine(settings=settings, url=read_engine_url(settings), read_only=True)
    async with engine.connect() as connection:
        first = await connection.scalar(sa.text("SELECT transaction_timestamp()"))
        second = await connection.scalar(sa.text("SELECT transaction_timestamp()"))
    assert first != second
    await engine.dispose()


async def test_read_engine_rejects_writes() -> None:
    engine = create_sa_engine(settings=settings, url=read_engine_url(settings), read_only=True)
    async with engine.connect() as connection:
        with pytest.raises(DBAPIError, match="read-only transaction"):
            await connection.execute(sa.insert(models.Deck).values(name="read only"))
    await engine.dispose()
