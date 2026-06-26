import typing

import fastapi
from modern_di_fastapi import FromDI

from app import models, schemas
from app.repositories import CardsRepository


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/{deck_id}/cards/")
async def list_cards(
    deck_id: int,
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Cards:
    objects = await cards_repository.list_for_deck(deck_id)
    return schemas.Cards.from_models(objects)


@ROUTER.get("/cards/{card_id}/")
async def get_card(
    card_id: int,
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Card:
    instance = await cards_repository.get_one(models.Card.id == card_id)
    return schemas.Card.model_validate(instance)


@ROUTER.post("/decks/{deck_id}/cards/")
async def create_cards(
    deck_id: int,
    data: list[schemas.CardCreate],
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Cards:
    objects = await cards_repository.add_cards(deck_id, data)
    return schemas.Cards.from_models(objects)


@ROUTER.put("/decks/{deck_id}/cards/")
async def update_cards(
    deck_id: int,
    data: list[schemas.Card],
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Cards:
    objects = await cards_repository.upsert_cards(deck_id, data)
    return schemas.Cards.from_models(objects)
