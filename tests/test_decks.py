import pytest
from fastapi import status
from httpx import AsyncClient
from that_depends import Provide, inject

from app import ioc
from app.repositories import CardsService, DecksService
from tests import factories


async def test_get_decks_empty(client: AsyncClient) -> None:
    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0


async def test_get_decks_not_exist(client: AsyncClient) -> None:
    response = await client.get("/api/decks/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@inject
async def test_get_decks(
    client: AsyncClient,
    decks_service: DecksService = Provide[ioc.IOCContainer.decks_service],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_service.create(deck)

    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(deck, k)


@inject
async def test_get_one_deck(
    client: AsyncClient,
    decks_service: DecksService = Provide[ioc.IOCContainer.decks_service],
    cards_service: CardsService = Provide[ioc.IOCContainer.cards_service],
) -> None:
    deck = await decks_service.create(factories.DeckModelFactory.build())
    card = await cards_service.create(factories.CardModelFactory.build(deck_id=deck.id))
    assert card.id
    cards_service.repository.session.expunge_all()

    response = await client.get(f"/api/decks/{deck.id}/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["cards"]) == 1
    for k, v in data.items():
        if k == "cards":
            continue
        assert v == getattr(deck, k)


@pytest.mark.parametrize(
    ("name", "description", "status_code"),
    [
        (None, None, status.HTTP_422_UNPROCESSABLE_ENTITY),
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


@inject
async def test_put_decks_wrong_body(
    client: AsyncClient,
    decks_service: DecksService = Provide[ioc.IOCContainer.decks_service],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_service.create(deck)

    # update deck
    response = await client.put(
        f"/api/decks/{deck.id}/",
        json={"name": None, "description": None},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


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
@inject
async def test_put_decks(
    client: AsyncClient,
    name: str,
    description: str,
    decks_service: DecksService = Provide[ioc.IOCContainer.decks_service],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_service.create(deck)

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
