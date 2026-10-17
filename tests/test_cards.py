import datetime
from typing import TYPE_CHECKING

import pytest
import sqlalchemy as sa
from fastapi import status

from app import models, schemas
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
    assert created_data["items"] == data["items"]
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


async def test_update_cards_does_not_move_a_card_from_another_deck(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    deck, other_deck = await factories.DeckModelFactory.create_batch_async(size=2)
    card = await factories.CardModelFactory.create_async(deck_id=other_deck.id)

    response = await client.put(f"/api/decks/{deck.id}/cards/", json=[{"id": card.id, "front": "moved"}])
    assert response.status_code == status.HTTP_404_NOT_FOUND
    stored = (
        await db_session.execute(sa.select(models.Card.deck_id, models.Card.front).where(models.Card.id == card.id))
    ).one()
    assert stored == (other_deck.id, card.front)


async def test_update_cards_with_an_unknown_id_inserts_nothing(client: AsyncClient, db_session: AsyncSession) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.put(f"/api/decks/{deck.id}/cards/", json=[{"id": card.id + 1, "front": "via put"}])
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (await db_session.scalars(sa.select(models.Card.front).where(models.Card.deck_id == deck.id))).all() == [
        card.front
    ]

    response = await client.post(f"/api/decks/{deck.id}/cards/", json=[{"front": "via post"}])
    assert response.status_code == status.HTTP_200_OK


async def test_update_cards_with_one_unknown_id_updates_nothing(client: AsyncClient, db_session: AsyncSession) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.put(
        f"/api/decks/{deck.id}/cards/",
        json=[{"id": card.id, "front": "updated"}, {"id": card.id + 1, "front": "unknown"}],
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (await db_session.scalars(sa.select(models.Card.front).where(models.Card.id == card.id))).one() == card.front


async def test_update_cards_rejects_duplicate_ids(client: AsyncClient, statements: list[str]) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card = await factories.CardModelFactory.create_async(deck_id=deck.id)
    statements.clear()

    response = await client.put(
        f"/api/decks/{deck.id}/cards/",
        json=[{"id": card.id, "front": "first"}, {"id": card.id, "front": "second"}],
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert statements == []


async def test_openapi_card_deck_id_required(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    card_schema = response.json()["components"]["schemas"]["Card"]
    assert "deck_id" in card_schema["required"]
    assert "null" not in {x.get("type") for x in card_schema["properties"]["deck_id"].get("anyOf", [])}


async def test_list_cards_pages_by_id_within_deck(client: AsyncClient) -> None:
    deck, other_deck = await factories.DeckModelFactory.create_batch_async(size=2)
    first, second = await factories.CardModelFactory.create_batch_async(size=2, deck_id=deck.id)
    await factories.CardModelFactory.create_async(deck_id=other_deck.id)
    third = await factories.CardModelFactory.create_async(deck_id=deck.id)

    response = await client.get(f"/api/decks/{deck.id}/cards/", params={"limit": 2})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [x["id"] for x in data["items"]] == [first.id, second.id]
    assert data["next_after"] == second.id

    response = await client.get(f"/api/decks/{deck.id}/cards/", params={"limit": 2, "after": data["next_after"]})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert [x["id"] for x in data["items"]] == [third.id]
    assert data["next_after"] is None


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"after": 0}])
async def test_list_cards_rejects_bad_page_params(client: AsyncClient, params: dict[str, int | str]) -> None:
    deck = await factories.DeckModelFactory.create_async()

    response = await client.get(f"/api/decks/{deck.id}/cards/", params=params)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_create_cards_in_a_missing_deck(client: AsyncClient) -> None:
    response = await client.post("/api/decks/999/cards/", json=[{"front": "orphan"}])
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("method", ["post", "put"])
async def test_card_writes_reject_too_many_cards(client: AsyncClient, statements: list[str], method: str) -> None:
    deck = await factories.DeckModelFactory.create_async()
    statements.clear()

    cards = [{"id": i, "front": str(i)} for i in range(1, schemas.MAX_CARDS_PER_REQUEST + 2)]
    response = await client.request(method, f"/api/decks/{deck.id}/cards/", json=cards)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert statements == []


async def test_update_cards_sends_the_same_sql_for_any_number_of_cards(
    client: AsyncClient, statements: list[str]
) -> None:
    deck = await factories.DeckModelFactory.create_async()
    card1, card2 = await factories.CardModelFactory.create_batch_async(size=2, deck_id=deck.id)
    statements.clear()

    response = await client.put(f"/api/decks/{deck.id}/cards/", json=[{"id": card1.id, "front": "one"}])
    assert response.status_code == status.HTTP_200_OK
    response = await client.put(
        f"/api/decks/{deck.id}/cards/",
        json=[{"id": card1.id, "front": "first"}, {"id": card2.id, "front": "second"}],
    )
    assert response.status_code == status.HTTP_200_OK
    assert [x["front"] for x in response.json()["items"]] == ["first", "second"]
    assert len(statements) == 2  # noqa: PLR2004
    assert statements[0] == statements[1]


@pytest.mark.parametrize(
    ("method", "path", "body", "params"),
    [
        ("get", f"/api/cards/{2**63}/", None, None),
        ("get", f"/api/decks/{2**63}/cards/", None, None),
        ("get", "/api/decks/1/cards/", None, {"after": 2**63}),
        ("post", f"/api/decks/{2**63}/cards/", [{"front": "x"}], None),
        ("put", "/api/decks/1/cards/", [{"id": 2**63, "front": "x"}], None),
    ],
)
async def test_card_endpoints_reject_ids_out_of_bigint_range(
    client: AsyncClient,
    method: str,
    path: str,
    body: list[dict[str, int | str]] | None,
    params: dict[str, int] | None,
) -> None:
    response = await client.request(method, path, json=body, params=params)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
