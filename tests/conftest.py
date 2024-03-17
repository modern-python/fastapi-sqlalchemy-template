import asyncio
import typing

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import application
from app.db.base import engine
from app.db.deps import session_context_var, set_db


@pytest.fixture(scope="session")
def event_loop(request: pytest.FixtureRequest) -> typing.Iterator[asyncio.AbstractEventLoop]:  # noqa: ARG001
    """Redefined event loop fixture with bigger scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def db() -> typing.AsyncIterator[AsyncSession]:
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False, future=True)
    await connection.begin_nested()
    try:
        yield session
    finally:
        if session.in_transaction():
            await transaction.rollback()
        await connection.close()


@pytest.fixture(name="db_context", autouse=True)
def _db_context(db: AsyncSession) -> typing.Iterator[None]:
    token = session_context_var.set(db)
    yield
    session_context_var.reset(token)


@pytest.fixture()
async def client() -> typing.AsyncIterator[AsyncClient]:
    def _set_db() -> None:
        return None

    application.dependency_overrides[set_db] = _set_db
    async with AsyncClient(
        app=application,
        base_url="http://test",
    ) as client:
        yield client
