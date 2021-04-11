import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.apps.decks import models
from tests.decks.conftest import get_deck_data


@pytest.mark.asyncio
def test_get_decks_empty(client: TestClient):
    response = client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0

    response = client.get("/api/decks/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
def test_get_decks(client: TestClient, deck: models.Deck):
    response = client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(deck, k)

    response = client.get(f"/api/decks/{deck.id}")
    assert response.status_code == status.HTTP_200_OK
    for k, v in response.json().items():
        assert v == getattr(deck, k)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,description,status_code",
    [
        (None, None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("test deck", None, status.HTTP_200_OK),
        ("test deck", "test deck description", status.HTTP_200_OK),
    ],
)
def test_post_decks(
    client: TestClient,
    name: str,
    description: str,
    status_code: int,
):
    # create deck
    response = client.post(
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
        response = client.get(f"/api/decks/{item_id}/")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert item_id == result["id"]
        assert name == result["name"]
        assert description == result["description"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name,description,status_code",
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
def test_put_decks(
    client: TestClient,
    deck: models.Deck,
    name: str,
    description: str,
    status_code: int,
):
    # update deck
    response = client.put(
        f"/api/decks/{deck.id}/",
        json={"name": name, "description": description},
    )
    assert response.status_code == status_code

    # get item
    if status_code == status.HTTP_200_OK:
        item_id = response.json()["id"]
        response = client.get(f"/api/decks/{item_id}/")
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert name == result["name"]
        assert description == result["description"]
