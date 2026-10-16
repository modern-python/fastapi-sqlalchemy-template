import asyncio
import typing
import uuid

import sqlalchemy as sa
from db_retry import Transaction

from app import models, schemas
from app.repositories import DecksRepository
from app.resources.db import create_primary_sa_engine, create_session
from app.use_cases.create_deck import CreateDeckUseCase


if typing.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


async def _wait_until_blocked_on_a_lock(engine: AsyncEngine, pid: int) -> None:
    wait_event_type = None
    while wait_event_type != "Lock":
        await asyncio.sleep(0.01)
        async with engine.connect() as connection:
            wait_event_type = await connection.scalar(
                sa.text("SELECT wait_event_type FROM pg_stat_activity WHERE pid = :pid"), {"pid": pid}
            )


async def test_create_deck_returns_the_deck_a_concurrent_request_created_with_the_same_key() -> None:
    engine: typing.Final = create_primary_sa_engine()
    idempotency_key: typing.Final = uuid.uuid4()
    try:
        async with engine.connect() as concurrent_request:
            await concurrent_request.execute(
                sa.insert(models.Deck).values(idempotency_key=idempotency_key, name="first")
            )
            session: typing.Final = create_session(engine)
            pid: typing.Final = await (await session.connection()).scalar(sa.text("SELECT pg_backend_pid()"))
            use_case: typing.Final = CreateDeckUseCase(
                transaction=Transaction(session=session), decks_repository=DecksRepository(session=session)
            )
            pending: typing.Final = asyncio.create_task(
                use_case(data=schemas.DeckCreate(idempotency_key=idempotency_key, name="second"))
            )
            await asyncio.wait_for(_wait_until_blocked_on_a_lock(engine, pid), timeout=5)
            await concurrent_request.commit()
            deck: typing.Final = await pending
        assert deck.name == "first"
    finally:
        async with engine.begin() as connection:
            await connection.execute(sa.delete(models.Deck).where(models.Deck.idempotency_key == idempotency_key))
        await engine.dispose()
