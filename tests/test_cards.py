import datetime
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


async def test_get_cards_empty(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()

    response = await client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0

    response = await client.get("/api/cards/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_cards(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.get(f"/api/decks/{card.deck_id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(card, k)


async def test_get_card(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.get(f"/api/cards/{card.id}/")
    assert response.status_code == status.HTTP_200_OK
    for k, v in response.json().items():
        assert v == getattr(card, k)


async def test_get_card_not_exist(client: AsyncClient) -> None:
    response = await client.get("/api/cards/999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_create_cards(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()

    cards_to_create = [factories.CardCreateSchemaFactory.build(), factories.CardCreateSchemaFactory.build()]
    response = await client.post(
        f"/api/decks/{deck.id}/cards/",
        json=[x.model_dump() for x in cards_to_create],
    )
    assert response.status_code == status.HTTP_200_OK
    created_data = response.json()

    # check creation
    response = await client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert created_data == data
    assert len(data["items"]) == len(cards_to_create)
    for k, v in cards_to_create[0].model_dump().items():
        assert data["items"][0][k] == v
    for k, v in cards_to_create[1].model_dump().items():
        assert data["items"][1][k] == v

    # unique constraint error
    response = await client.post(
        f"/api/decks/{deck.id}/cards/",
        json=[cards_to_create[0].model_dump(), cards_to_create[1].model_dump()],
    )
    data = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert data["detail"] == "A record matching the supplied data already exists."


async def test_update_cards(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card1, card2 = await factories.CardModelFactory.create_batch_async(size=2, deck_id=deck.id)

    updated_data = [
        {
            "id": card1.id,
            "front": "card front updated",
            "back": "card back updated",
            "hint": "card hint updated",
        },
        {
            "id": card2.id,
            "front": "card front2 updated",
            "back": "card back2 updated",
            "hint": "card hint2 updated",
        },
    ]
    response = await client.put(
        f"/api/decks/{deck.id}/cards/",
        json=updated_data,
    )
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()["items"]
    for x in cards:
        assert x.pop("deck_id") == deck.id
    assert cards == updated_data

    # check creation
    response = await client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()["items"]
    assert len(cards) == len(updated_data)
    for x in cards:
        assert x.pop("deck_id") == deck.id
    assert cards == updated_data


async def test_cards_ordered_by_id_after_update(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card1, card2 = await factories.CardModelFactory.create_batch_async(size=2, deck_id=deck.id)

    response = await client.put(
        f"/api/decks/{deck.id}/cards/",
        json=[{"id": card2.id, "front": "card2 updated"}, {"id": card1.id, "front": "card1 updated"}],
    )
    assert response.status_code == status.HTTP_200_OK
    assert [x["id"] for x in response.json()["items"]] == [card1.id, card2.id]

    response = await client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    assert [x["id"] for x in response.json()["items"]] == [card1.id, card2.id]


async def test_update_cards_sends_one_statement(client: AsyncClient, statements: list[str]) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card1, card2 = await factories.CardModelFactory.create_batch_async(size=2, deck_id=deck.id)
    statements.clear()

    response = await client.put(
        f"/api/decks/{deck.id}/cards/",
        json=[{"id": card1.id, "front": "card1 updated"}, {"id": card2.id, "front": "card2 updated"}],
    )
    assert response.status_code == status.HTTP_200_OK
    assert [x["front"] for x in response.json()["items"]] == ["card1 updated", "card2 updated"]
    assert len(statements) == 1


async def test_update_cards_moves_updated_at(client: AsyncClient, db_session: AsyncSession) -> None:
    long_ago = datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id, updated_at=long_ago)

    response = await client.put(f"/api/decks/{deck.id}/cards/", json=[{"id": card.id, "front": "updated"}])
    assert response.status_code == status.HTTP_200_OK
    updated_at = (await db_session.scalars(sa.select(models.Card.updated_at).where(models.Card.id == card.id))).one()
    assert updated_at > long_ago


async def test_update_cards_with_no_cards(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()

    response = await client.put(f"/api/decks/{deck.id}/cards/", json=[])
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"items": []}


async def test_update_cards_to_a_duplicate_front(client: AsyncClient) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card1, card2 = await factories.CardModelFactory.create_batch_async(size=2, deck_id=deck.id)

    response = await client.put(f"/api/decks/{deck.id}/cards/", json=[{"id": card2.id, "front": card1.front}])
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_openapi_card_deck_id_required(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    card_schema = response.json()["components"]["schemas"]["Card"]
    assert "deck_id" in card_schema["required"]
    assert "null" not in {x.get("type") for x in card_schema["properties"]["deck_id"].get("anyOf", [])}
