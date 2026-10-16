import asyncio
import inspect
import typing

import asyncpg
import modern_di
import pytest
import sqlalchemy as sa
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

from app import ioc, models, schemas
from app.api import cards, decks
from app.resources.db import create_primary_sa_engine, create_read_sa_engine


if typing.TYPE_CHECKING:
    from httpx import AsyncClient


class StoredIds(typing.NamedTuple):
    deck_id: int
    card_id: int


async def _truncate(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(sa.text("TRUNCATE cards, decks RESTART IDENTITY"))


@pytest.fixture
async def stored_ids() -> typing.AsyncIterator[StoredIds]:
    engine: typing.Final = create_primary_sa_engine()
    await _truncate(engine)
    async with engine.begin() as connection:
        deck_id: typing.Final = (
            await connection.execute(sa.insert(models.Deck).values(name="deck").returning(models.Deck.id))
        ).scalar_one()
        card_id: typing.Final = (
            await connection.execute(
                sa.insert(models.Card).values(front="front", deck_id=deck_id).returning(models.Card.id)
            )
        ).scalar_one()
    try:
        yield StoredIds(deck_id=deck_id, card_id=card_id)
    finally:
        await _truncate(engine)
        await engine.dispose()


@pytest.fixture
async def engines(di_container: modern_di.Container) -> typing.AsyncIterator[tuple[AsyncEngine, AsyncEngine]]:
    primary_engine: typing.Final = create_primary_sa_engine()
    read_engine: typing.Final = create_read_sa_engine()
    di_container.override(ioc.Dependencies.database_engine, primary_engine)
    di_container.override(ioc.Dependencies.database_read_engine, read_engine)
    try:
        yield primary_engine, read_engine
    finally:
        di_container.reset_override()
        await primary_engine.dispose()
        await read_engine.dispose()


@pytest.fixture
async def request_container(di_container: modern_di.Container) -> typing.AsyncIterator[modern_di.Container]:
    async with di_container.build_child_container(scope=modern_di.Scope.REQUEST) as container:
        yield container


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


@pytest.fixture
async def lost_connection(engines: tuple[AsyncEngine, AsyncEngine], request_container: modern_di.Container) -> None:
    """Leave the request session holding a primary connection whose backend was terminated."""
    session: typing.Final = request_container.resolve_provider(ioc.Dependencies.session)
    assert isinstance(session, AsyncSession)
    connection: typing.Final = await session.connection()
    primary_engine, _ = engines
    await _terminate_backend(primary_engine, *await _watch_backend(connection))


@pytest.fixture
async def lost_pooled_connection(engines: tuple[AsyncEngine, AsyncEngine]) -> None:
    """Leave each engine's pool holding one idle connection whose backend was terminated."""
    for engine in engines:
        async with engine.connect() as connection:
            watched = await _watch_backend(connection)
        await _terminate_backend(engine, *watched)


@pytest.mark.usefixtures("lost_pooled_connection")
@pytest.mark.parametrize(
    "build_request",
    [
        lambda _: ("GET", "/api/decks/", None),
        lambda ids: ("GET", f"/api/decks/{ids.deck_id}/", None),
        lambda ids: ("PUT", f"/api/decks/{ids.deck_id}/", {"name": "renamed"}),
        lambda _: ("POST", "/api/decks/", {"name": "new"}),
        lambda ids: ("GET", f"/api/decks/{ids.deck_id}/cards/", None),
        lambda ids: ("GET", f"/api/cards/{ids.card_id}/", None),
        lambda ids: ("POST", f"/api/decks/{ids.deck_id}/cards/", [{"front": "new"}]),
        lambda ids: ("PUT", f"/api/decks/{ids.deck_id}/cards/", [{"id": ids.card_id, "front": "renamed"}]),
    ],
)
async def test_endpoint_recovers_from_a_connection_lost_while_pooled(
    client: AsyncClient,
    stored_ids: StoredIds,
    build_request: typing.Callable[[StoredIds], tuple[str, str, object]],
) -> None:
    method, path, json = build_request(stored_ids)
    response: typing.Final = await client.request(method, path, json=json)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("lost_connection")
@pytest.mark.parametrize(
    ("handler", "build_kwargs"),
    [
        (decks.list_decks, lambda _: {}),
        (decks.get_deck, lambda ids: {"deck_id": ids.deck_id}),
        (decks.update_deck, lambda ids: {"deck_id": ids.deck_id, "data": schemas.DeckCreate(name="renamed")}),
        (decks.create_deck, lambda _: {"data": schemas.DeckCreate(name="new")}),
        (cards.list_cards, lambda ids: {"deck_id": ids.deck_id}),
        (cards.get_card, lambda ids: {"card_id": ids.card_id}),
        (cards.create_cards, lambda ids: {"deck_id": ids.deck_id, "data": [schemas.CardCreate(front="new")]}),
        (
            cards.update_cards,
            lambda ids: {"deck_id": ids.deck_id, "data": [schemas.Card(id=ids.card_id, front="renamed")]},
        ),
    ],
)
async def test_handler_recovers_from_a_lost_connection(
    request_container: modern_di.Container,
    stored_ids: StoredIds,
    handler: typing.Callable[..., typing.Awaitable[schemas.Base]],
    build_kwargs: typing.Callable[[StoredIds], dict[str, typing.Any]],
) -> None:
    dependencies: typing.Final = {
        "decks_repository": request_container.resolve_provider(ioc.Dependencies.decks_repository),
        "cards_repository": request_container.resolve_provider(ioc.Dependencies.cards_repository),
        "transaction": request_container.resolve_provider(ioc.Dependencies.transaction),
    }
    parameters: typing.Final = inspect.signature(handler).parameters
    kwargs: typing.Final = {name: value for name, value in dependencies.items() if name in parameters}
    assert isinstance(await handler(**kwargs, **build_kwargs(stored_ids)), schemas.Base)
