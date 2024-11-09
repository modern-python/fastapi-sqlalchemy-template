from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests import factories


async def test_get_cards_empty(client: AsyncClient, db_session: AsyncSession) -> None:
    factories.DeckModelFactory.__async_session__ = db_session
    deck = await factories.DeckModelFactory.create_async()

    response = await client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0

    response = await client.get("/api/cards/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_cards(client: AsyncClient, db_session: AsyncSession) -> None:
    factories.DeckModelFactory.__async_session__ = db_session
    factories.CardModelFactory.__async_session__ = db_session
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.get(f"/api/decks/{card.deck_id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(card, k)


async def test_get_card(client: AsyncClient, db_session: AsyncSession) -> None:
    factories.DeckModelFactory.__async_session__ = db_session
    factories.CardModelFactory.__async_session__ = db_session
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.get(f"/api/cards/{card.id}/")
    assert response.status_code == status.HTTP_200_OK
    for k, v in response.json().items():
        assert v == getattr(card, k)


async def test_get_card_not_exist(client: AsyncClient) -> None:
    response = await client.get("/api/cards/999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_create_cards(client: AsyncClient, db_session: AsyncSession) -> None:
    factories.DeckModelFactory.__async_session__ = db_session
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
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"] == "A record matching the supplied data already exists."


async def test_update_cards(client: AsyncClient, db_session: AsyncSession) -> None:
    factories.DeckModelFactory.__async_session__ = db_session
    factories.CardModelFactory.__async_session__ = db_session
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
