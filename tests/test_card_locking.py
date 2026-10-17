import asyncio
import typing
import uuid

import sqlalchemy as sa
from fastapi import status

from app import models


if typing.TYPE_CHECKING:
    from httpx import AsyncClient, Response
    from sqlalchemy.ext.asyncio import AsyncEngine


async def wait_for_lock_waiters(engine: AsyncEngine, count: int, request: asyncio.Task[typing.Any]) -> None:
    statement: typing.Final = sa.text(
        "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database() AND wait_event_type = 'Lock'"
    )
    async with asyncio.timeout(5):
        while not request.done():
            async with engine.connect() as connection:
                if await connection.scalar(statement) >= count:
                    return
            await asyncio.sleep(0.01)


async def test_concurrent_card_updates_in_opposite_orders_do_not_deadlock(
    client: AsyncClient, committing_engine: AsyncEngine
) -> None:
    async with committing_engine.begin() as connection:
        deck_id = await connection.scalar(
            sa.insert(models.Deck).values(name="locking", idempotency_key=uuid.uuid4()).returning(models.Deck.id)
        )
        card1, card2, card3 = (
            await connection.scalars(
                sa.insert(models.Card)
                .values([{"deck_id": deck_id, "front": f"card{i}"} for i in range(1, 4)])
                .returning(models.Card.id)
            )
        ).all()
    url: typing.Final = f"/api/decks/{deck_id}/cards/"
    requests: typing.Final[list[asyncio.Task[Response]]] = []
    try:
        async with committing_engine.connect() as blocker:
            await blocker.execute(sa.text("SELECT 1 FROM cards WHERE id = :id FOR UPDATE"), {"id": card3})
            requests.append(
                asyncio.create_task(
                    client.put(
                        url,
                        json=[
                            {"id": card1, "front": "a1"},
                            {"id": card3, "front": "a3"},
                            {"id": card2, "front": "a2"},
                        ],
                    )
                )
            )
            await wait_for_lock_waiters(committing_engine, 1, requests[0])
            requests.append(
                asyncio.create_task(client.put(url, json=[{"id": card2, "front": "b2"}, {"id": card1, "front": "b1"}]))
            )
            await wait_for_lock_waiters(committing_engine, 2, requests[1])
        responses = await asyncio.gather(*requests)
    finally:
        for request in requests:
            request.cancel()
        await asyncio.gather(*requests, return_exceptions=True)
        async with committing_engine.begin() as connection:
            await connection.execute(sa.delete(models.Card).where(models.Card.deck_id == deck_id))
            await connection.execute(sa.delete(models.Deck).where(models.Deck.id == deck_id))

    assert [response.status_code for response in responses] == [status.HTTP_200_OK, status.HTTP_200_OK]
