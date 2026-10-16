import asyncio
import typing

import asyncpg
import modern_di
import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

from app import ioc
from app.resources.db import create_primary_sa_engine


@pytest.fixture
async def request_container(di_container: modern_di.Container) -> typing.AsyncIterator[modern_di.Container]:
    engine: typing.Final = create_primary_sa_engine()
    di_container.override(ioc.Database.database_engine, engine)
    try:
        async with di_container.build_child_container(scope=modern_di.Scope.REQUEST) as container:
            yield container
    finally:
        di_container.reset_override()
        await engine.dispose()


async def _watch_backend(connection: AsyncConnection) -> tuple[int, asyncio.Event]:
    pid: typing.Final = await connection.scalar(sa.text("SELECT pg_backend_pid()"))
    driver_connection: typing.Final = (await connection.get_raw_connection()).driver_connection
    assert driver_connection is not None
    closed: typing.Final = asyncio.Event()
    driver_connection.add_termination_listener(lambda _: closed.set())
    return pid, closed


async def _terminate_backend(engine: AsyncEngine, pid: int, closed: asyncio.Event) -> None:
    killer: typing.Final = await asyncpg.connect(
        engine.url.set(drivername="postgresql").render_as_string(hide_password=False)
    )
    try:
        await killer.execute("SELECT pg_terminate_backend($1)", pid)
    finally:
        await killer.close()
    await asyncio.wait_for(closed.wait(), timeout=5)


@pytest.fixture(params=["held_by_session", "idle_in_pool"])
async def lost_connection(request: pytest.FixtureRequest, request_container: modern_di.Container) -> None:
    """Terminate the backend of the connection the request session holds, or of an idle pooled one."""
    engine: typing.Final = request_container.resolve_provider(ioc.Database.database_engine)
    assert isinstance(engine, AsyncEngine)
    if request.param == "held_by_session":
        session: typing.Final = request_container.resolve_provider(ioc.Database.session)
        assert isinstance(session, AsyncSession)
        watched = await _watch_backend(await session.connection())
    else:
        async with engine.connect() as connection:
            watched = await _watch_backend(connection)
    await _terminate_backend(engine, *watched)


@pytest.mark.usefixtures("lost_connection")
async def test_use_case_recovers_from_a_lost_connection(request_container: modern_di.Container) -> None:
    use_case: typing.Final = request_container.resolve_provider(ioc.UseCases.list_decks_use_case)
    assert await use_case() == []
