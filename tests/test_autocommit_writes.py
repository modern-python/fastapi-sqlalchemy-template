import contextlib
import typing
import uuid

import modern_di
import pytest
import sqlalchemy as sa
from advanced_alchemy.exceptions import NotFoundError
from sqlalchemy import event

from app import ioc, models, schemas
from app.resources.db import create_primary_sa_engine


if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


@pytest.fixture
async def primary_engine(di_container: modern_di.Container) -> typing.AsyncIterator[AsyncEngine]:
    engine = create_primary_sa_engine()
    di_container.override(ioc.Database.dynamic_engine, engine)
    try:
        yield engine
    finally:
        di_container.reset_override(ioc.Database.dynamic_engine)
        await engine.dispose()


@contextlib.contextmanager
def record_in_transaction(engine: AsyncEngine) -> typing.Iterator[list[bool]]:
    in_transaction: typing.Final[list[bool]] = []

    def record(connection: sa.Connection, *_: object) -> None:
        driver_connection = connection.connection.driver_connection
        assert driver_connection is not None
        in_transaction.append(driver_connection.is_in_transaction())

    event.listen(engine.sync_engine, "after_cursor_execute", record)
    try:
        yield in_transaction
    finally:
        event.remove(engine.sync_engine, "after_cursor_execute", record)


async def test_create_deck_sends_no_begin_or_commit(
    di_container: modern_di.Container, primary_engine: AsyncEngine
) -> None:
    key: typing.Final = uuid.uuid4()
    try:
        with record_in_transaction(primary_engine) as in_transaction:
            async with di_container.build_child_container(scope=modern_di.Scope.REQUEST) as container:
                use_case = container.resolve_provider(ioc.UseCases.create_deck_use_case)
                await use_case(data=schemas.DeckCreate(name="autocommit", idempotency_key=key))
    finally:
        async with primary_engine.begin() as connection:
            await connection.execute(sa.delete(models.Deck).where(models.Deck.idempotency_key == key))

    assert in_transaction == [False]


async def test_update_deck_sends_no_begin_or_commit(
    di_container: modern_di.Container, primary_engine: AsyncEngine
) -> None:
    with record_in_transaction(primary_engine) as in_transaction:
        async with di_container.build_child_container(scope=modern_di.Scope.REQUEST) as container:
            use_case = container.resolve_provider(ioc.UseCases.update_deck_use_case)
            with pytest.raises(NotFoundError):
                await use_case(deck_id=-1, data=schemas.DeckUpdate(name="autocommit"))

    assert in_transaction == [False]
