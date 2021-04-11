import pytest

from app.apps.decks import models, schemas


@pytest.fixture
async def deck(db):
    deck_data = schemas.DeckCreate(**get_deck_data())
    deck = models.Deck(**deck_data.dict())
    await deck.save(db)
    return deck


def get_deck_data():
    return {"name": "test deck", "description": "test deck description"}


@pytest.fixture
async def card(db, deck: models.Deck):
    instance = models.Card(**card_data.dict(), deck_id=deck.id)
    await instance.save(db)
    return instance


@pytest.fixture
async def another_card(db, deck: models.Deck):
    instance = models.Card(**another_card_data.dict(), deck_id=deck.id)
    await instance.save(db)
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
