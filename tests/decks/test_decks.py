import pytest
from fastapi import status
from httpx import AsyncClient

from app.apps.decks import models
from tests.decks.conftest import get_deck_data


pytestmark = pytest.mark.asyncio


async def test_get_decks_empty(client: AsyncClient) -> None:
    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0


async def test_get_decks_not_exist(client: AsyncClient) -> None:
    response = await client.get("/api/decks/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_decks(client: AsyncClient, deck: models.Deck) -> None:
    response = await client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(deck, k)


@pytest.mark.usefixtures("card")
async def test_get_deck(client: AsyncClient, deck: models.Deck) -> None:
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


@pytest.mark.parametrize(
    ("name", "description", "status_code"),
    [
        (None, None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("test deck updated", None, status.HTTP_200_OK),
        (
            get_deck_data()["name"],
            "test deck description updated",
            status.HTTP_200_OK,
        ),
        (
            "test deck updated",
            "test deck description updated",
            status.HTTP_200_OK,
        ),
    ],
)
async def test_put_decks(
    client: AsyncClient,
    deck: models.Deck,
    name: str,
    description: str,
    status_code: int,
) -> None:
    # update deck
    response = await client.put(
        f"/api/decks/{deck.id}/",
        json={"name": name, "description": description},
    )
    assert response.status_code == status_code

    # get item
    if status_code == status.HTTP_200_OK:
        item_id = response.json()["id"]
        response = await client.get(f"/api/decks/{item_id}/")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert name == result["name"]
        assert description == result["description"]
