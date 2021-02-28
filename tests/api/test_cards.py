import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app import models
from tests import test_data


@pytest.mark.asyncio
def test_get_cards_empty(client: TestClient, deck: models.Deck):
    response = client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["cards"]) == 0

    response = client.get(f"/api/decks/{deck.id}/cards/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
def test_get_cards(client: TestClient, card: models.Card):
    response = client.get(f"/api/decks/{card.deck_id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["cards"]) == 1
    for k, v in data["cards"][0].items():
        assert v == getattr(card, k)

    response = client.get(f"/api/cards/{card.id}/")
    assert response.status_code == status.HTTP_200_OK
    for k, v in response.json().items():
        assert v == getattr(card, k)


@pytest.mark.asyncio
def test_create_cards(client: TestClient, deck: models.Deck):
    # bulk create
    response = client.post(
        f"/api/decks/{deck.id}/cards/",
        json=[test_data.card.dict(), test_data.card2.dict()],
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # check creation
    response = client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["cards"]) == 2

    # unique constraint error
    response = client.post(
        f"/api/decks/{deck.id}/cards/",
        json=[test_data.card.dict(), test_data.card2.dict()],
    )
    data = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["msg"] == "Unique constraint violated for Card"
    assert data["detail"][0]["loc"] == ["deck_id, front"]


@pytest.mark.asyncio
def test_update_cards(
    client: TestClient, deck: models.Deck, card: models.Card, card2: models.Card
):
    updated_data = [
        {
            "id": card.id,
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
    response = client.put(
        f"/api/decks/{deck.id}/cards/",
        json=updated_data,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # check creation
    response = client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()["cards"]
    assert len(cards) == 2
    for x in cards:
        del x["deck_id"]
    assert cards == updated_data
