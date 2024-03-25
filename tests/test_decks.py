import pytest
from fastapi import status
from httpx import AsyncClient
from that_depends import Provide, inject

from app import ioc
from app.repositories.decks import CardsRepository, DecksRepository
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
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    assert str(deck) == "<Deck(self.id=None)>"
    await decks_repo.save(deck)

    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(deck, k)


@inject
async def test_get_deck(
    client: AsyncClient,
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
    cards_repo: CardsRepository = Provide[ioc.IOCContainer.cards_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

    card = factories.CardModelFactory.build(deck_id=deck.id)
    await cards_repo.save(card)

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
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

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
    decks_repo: DecksRepository = Provide[ioc.IOCContainer.decks_repo],
) -> None:
    deck = factories.DeckModelFactory.build()
    await decks_repo.save(deck)

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
