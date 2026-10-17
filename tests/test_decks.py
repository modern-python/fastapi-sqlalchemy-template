import datetime
import uuid
from typing import TYPE_CHECKING

import pytest
import sqlalchemy as sa
from fastapi import status

from app import models
from tests import factories


if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = [pytest.mark.usefixtures("set_async_session_in_base_sqlalchemy_factory")]


async def test_get_decks_empty(client: AsyncClient) -> None:
    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0


async def test_get_decks_not_exist(client: AsyncClient) -> None:
    response = await client.get("/api/decks/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_decks(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()

    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(deck, k)


async def test_list_decks_omits_cards(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()
    await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    item = response.json()["items"][0]
    assert "cards" not in item


async def test_list_decks_ordered_by_id_after_update(client: AsyncClient) -> None:
    deck1, deck2 = await factories.DeckModelFactory.create_batch_async(size=2)

    response = await client.put(f"/api/decks/{deck1.id}/", json={"name": "deck1 updated"})
    assert response.status_code == status.HTTP_200_OK

    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    assert [x["id"] for x in response.json()["items"]] == [deck1.id, deck2.id]


async def test_get_one_deck(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)
    assert card.id

    response = await client.get(f"/api/decks/{deck.id}/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["cards"]) == 1
    for k, v in data.items():
        if k == "cards":
            continue
        assert v == getattr(deck, k)


async def test_get_one_deck_loads_cards_in_one_query(client: AsyncClient, statements: list[str]) -> None:
    deck = await factories.DeckModelFactory.create_async()
    await factories.CardModelFactory.create_batch_async(size=2, deck_id=deck.id)
    statements.clear()

    response = await client.get(f"/api/decks/{deck.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["cards"]) == 2  # noqa: PLR2004
    assert len(statements) == 1


@pytest.mark.parametrize(
    ("name", "description", "status_code"),
    [
        (None, None, status.HTTP_422_UNPROCESSABLE_CONTENT),
        ("test deck", None, status.HTTP_200_OK),
        ("test deck", "test deck description", status.HTTP_200_OK),
    ],
)
async def test_post_decks(
    client: AsyncClient,
    name: str,
    description: str,
    status_code: int,
) -> None:
    # create deck
    response = await client.post(
        "/api/decks/",
        json={
            "idempotency_key": str(uuid.uuid4()),
            "name": name,
            "description": description,
        },
    )
    assert response.status_code == status_code

    # get item
    if status_code == status.HTTP_200_OK:
        item_id = response.json()["id"]
        response = await client.get(f"/api/decks/{item_id}/")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert item_id == result["id"]
        assert name == result["name"]
        assert description == result["description"]


async def test_put_decks_wrong_body(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()

    # update deck
    response = await client.put(
        f"/api/decks/{deck.id}/",
        json={"name": None, "description": None},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_put_decks_not_exist(client: AsyncClient) -> None:
    response = await client.put(
        "/api/decks/999/",
        json={"name": "some", "description": "some"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    ("name", "description"),
    [
        ("test deck updated", None),
        ("test deck updated", "test deck description updated"),
    ],
)
async def test_put_decks(client: AsyncClient, name: str, description: str) -> None:
    deck = await factories.DeckModelFactory.create_async()

    # update deck
    response = await client.put(
        f"/api/decks/{deck.id}/",
        json={"name": name, "description": description},
    )
    assert response.status_code == status.HTTP_200_OK

    # get item
    item_id = response.json()["id"]
    response = await client.get(f"/api/decks/{item_id}/")
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert name == result["name"]
    assert description == result["description"]


async def test_post_decks_requires_an_idempotency_key(client: AsyncClient) -> None:
    response = await client.post("/api/decks/", json={"name": "test deck"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_post_decks_twice_with_one_idempotency_key_creates_one_deck(client: AsyncClient) -> None:
    idempotency_key = str(uuid.uuid4())

    first = await client.post("/api/decks/", json={"idempotency_key": idempotency_key, "name": "first"})
    second = await client.post("/api/decks/", json={"idempotency_key": idempotency_key, "name": "second"})

    assert first.status_code == status.HTTP_200_OK
    assert second.status_code == status.HTTP_200_OK
    assert second.json() == first.json()
    response = await client.get("/api/decks/")
    assert [item["name"] for item in response.json()["items"]] == ["first"]


async def test_put_decks_sends_one_statement(client: AsyncClient, statements: list[str]) -> None:
    deck = await factories.DeckModelFactory.create_async()
    statements.clear()

    response = await client.put(f"/api/decks/{deck.id}/", json={"name": "renamed", "description": None})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"id": deck.id, "name": "renamed", "description": None}
    assert len(statements) == 1


async def test_put_decks_moves_updated_at(client: AsyncClient, db_session: AsyncSession) -> None:
    long_ago = datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)
    deck = await factories.DeckModelFactory.create_async(updated_at=long_ago)

    response = await client.put(f"/api/decks/{deck.id}/", json={"name": "renamed", "description": None})
    assert response.status_code == status.HTTP_200_OK
    updated_at = (await db_session.scalars(sa.select(models.Deck.updated_at).where(models.Deck.id == deck.id))).one()
    assert updated_at > long_ago


async def test_list_decks_first_page(client: AsyncClient) -> None:
    decks = await factories.DeckModelFactory.create_batch_async(size=3)

    response = await client.get("/api/decks/", params={"limit": 2})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [x["id"] for x in data["items"]] == [decks[0].id, decks[1].id]
    assert data["next_after"] == decks[1].id


async def test_list_decks_after_cursor(client: AsyncClient) -> None:
    decks = await factories.DeckModelFactory.create_batch_async(size=3)

    response = await client.get("/api/decks/", params={"limit": 2, "after": decks[1].id})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [x["id"] for x in data["items"]] == [decks[2].id]
    assert data["next_after"] is None


async def test_list_decks_exactly_limit_has_no_next_page(client: AsyncClient) -> None:
    decks = await factories.DeckModelFactory.create_batch_async(size=2)

    response = await client.get("/api/decks/", params={"limit": 2})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [x["id"] for x in data["items"]] == [x.id for x in decks]
    assert data["next_after"] is None


async def test_list_decks_default_limit(client: AsyncClient) -> None:
    decks = await factories.DeckModelFactory.create_batch_async(size=51)

    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [x["id"] for x in data["items"]] == [x.id for x in decks[:50]]
    assert data["next_after"] == decks[49].id


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"after": 0}, {"after": "x"}])
async def test_list_decks_rejects_bad_page_params(client: AsyncClient, params: dict[str, int | str]) -> None:
    response = await client.get("/api/decks/", params=params)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
