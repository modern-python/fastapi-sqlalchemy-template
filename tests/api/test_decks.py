import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app import models
from tests import test_data


@pytest.mark.asyncio
def test_get_decks_empty(client: TestClient):
    response = client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["decks"]) == 0

    response = client.get("/api/decks/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
def test_get_decks(client: TestClient, deck: models.Deck):
    response = client.get("/api/decks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["decks"]) == 1
    for k, v in data["decks"][0].items():
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
        (test_data.deck.name, None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("test deck 2", None, status.HTTP_200_OK),
        ("test deck 2", "test deck description", status.HTTP_200_OK),
    ],
)
def test_post_decks(
    client: TestClient,
    deck: models.Deck,
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

    # get list
    if status_code == status.HTTP_200_OK:
        item_id = response.json()["id"]
        response = client.get("/api/decks/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "decks" in data
        assert item_id in [x["id"] for x in data["decks"]]
