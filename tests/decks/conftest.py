import typing

import pytest

from app.apps.decks import models, schemas


@pytest.fixture()
async def deck() -> models.Deck:
    deck_data = schemas.DeckCreate(**get_deck_data())
    deck = models.Deck(**deck_data.dict())
    await deck.save()
    return deck


def get_deck_data() -> dict[str, typing.Any]:
    return {"name": "test deck", "description": "test deck description"}


@pytest.fixture()
async def card(deck: models.Deck) -> models.Card:
    instance = models.Card(**card_data.dict(), deck_id=deck.id)
    await instance.save()
    return instance


@pytest.fixture()
async def another_card(deck: models.Deck) -> models.Card:
    instance = models.Card(**another_card_data.dict(), deck_id=deck.id)
    await instance.save()
    return instance


card_data = schemas.CardCreate(
    front="card front",
    back="card back",
    hint="card hint",
)

another_card_data = schemas.CardCreate(
    front="another card front",
    back="another card back",
    hint="another card hint",
)
