from fastapi import status
from httpx import AsyncClient
from that_depends import Provide, inject

from app import ioc
from app.repositories.decks import CardsRepository, DecksRepository
from tests import factories


@inject
async def test_get_cards_empty(
    client: AsyncClient,
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

    response = await client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0

    response = await client.get(f"/api/decks/{deck.id}/cards/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@inject
async def test_get_cards(
    client: AsyncClient,
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
    cards_repo: CardsRepository = Provide[ioc.IOCContainer.cards_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

    card = factories.CardModelFactory.build(deck_id=deck.id)
    await cards_repo.save(card)

    response = await client.get(f"/api/decks/{card.deck_id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(card, k)


@inject
async def test_get_card(
    client: AsyncClient,
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
    cards_repo: CardsRepository = Provide[ioc.IOCContainer.cards_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

    card = factories.CardModelFactory.build(deck_id=deck.id)
    await cards_repo.save(card)

    response = await client.get(f"/api/cards/{card.id}/")
    assert response.status_code == status.HTTP_200_OK
    for k, v in response.json().items():
        assert v == getattr(card, k)


async def test_get_card_not_exist(client: AsyncClient) -> None:
    response = await client.get("/api/cards/999/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@inject
async def test_create_cards(
    client: AsyncClient,
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
) -> None:
    # bulk create
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

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
    assert data["detail"][0]["msg"] == "Unique constraint violated for Card"
    assert data["detail"][0]["loc"] == ["deck_id, front"]


@inject
async def test_update_cards(
    client: AsyncClient,
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
    cards_repo: CardsRepository = Provide[ioc.IOCContainer.cards_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

    card1 = factories.CardModelFactory.build(deck_id=deck.id)
    card2 = factories.CardModelFactory.build(deck_id=deck.id)
    await cards_repo.save(card1)
    await cards_repo.save(card2)

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
