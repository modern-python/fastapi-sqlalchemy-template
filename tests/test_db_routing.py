import typing

import fastapi
import pytest
from modern_di import Scope

from app import ioc
from app.resources.db import create_replica_sa_engine, create_sa_engine
from app.settings import settings


if typing.TYPE_CHECKING:
    import modern_di
    from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.fixture
async def primary_engine(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncEngine]:
    engine = create_sa_engine(settings.db_dsn_parsed)
    di_container.override(ioc.Dependencies.database_engine, engine)
    yield engine
    await engine.dispose()


@pytest.fixture
async def replica_engine(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncEngine]:
    engine = create_sa_engine(settings.db_dsn_parsed)
    di_container.override(ioc.Dependencies.database_replica_engine, engine)
    yield engine
    await engine.dispose()


def resolve_engine(di_container: modern_di.Container, method: str | None) -> AsyncEngine:
    context = {fastapi.Request: fastapi.Request({"type": "http", "method": method})} if method else None
    with di_container.build_child_container(scope=Scope.REQUEST, context=context) as request_container:
        return request_container.resolve_provider(ioc.Dependencies.dynamic_engine)


@pytest.mark.parametrize("method", ["GET", "HEAD"])
def test_safe_methods_use_replica(
    di_container: modern_di.Container, primary_engine: AsyncEngine, replica_engine: AsyncEngine, method: str
) -> None:
    engine = resolve_engine(di_container, method)
    assert engine is replica_engine
    assert engine is not primary_engine


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_write_methods_use_primary(
    di_container: modern_di.Container, primary_engine: AsyncEngine, replica_engine: AsyncEngine, method: str
) -> None:
    engine = resolve_engine(di_container, method)
    assert engine is primary_engine
    assert engine is not replica_engine


@pytest.mark.usefixtures("replica_engine")
def test_no_request_uses_primary(di_container: modern_di.Container, primary_engine: AsyncEngine) -> None:
    assert resolve_engine(di_container, None) is primary_engine


def test_no_replica_configured_uses_primary(di_container: modern_di.Container, primary_engine: AsyncEngine) -> None:
    assert di_container.resolve_provider(ioc.Dependencies.database_replica_engine) is None
    assert resolve_engine(di_container, "GET") is primary_engine


async def test_replica_engine_built_from_replica_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "db_replica_dsn", "postgresql+asyncpg://postgres:password@replica/postgres")
    engine = create_replica_sa_engine()
    assert engine
    assert engine.url.host == "replica"
    await engine.dispose()
