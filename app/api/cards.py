import typing

import fastapi
from db_retry import Transaction, postgres_retry
from modern_di_fastapi import FromDI

from app import models, schemas
from app.repositories import CardsRepository


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/{deck_id}/cards/")
@postgres_retry
async def list_cards(
    deck_id: int,
    cards_repository: CardsRepository = FromDI(CardsRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.Cards:
    async with transaction:
        objects = await cards_repository.list_for_deck(deck_id)
        await transaction.commit()
    return schemas.Cards.from_models(objects)


@ROUTER.get("/cards/{card_id}/")
@postgres_retry
async def get_card(
    card_id: int,
    cards_repository: CardsRepository = FromDI(CardsRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.Card:
    async with transaction:
        instance = await cards_repository.get_one(models.Card.id == card_id)
        await transaction.commit()
    return schemas.Card.model_validate(instance)


@ROUTER.post("/decks/{deck_id}/cards/")
@postgres_retry
async def create_cards(
    deck_id: int,
    data: list[schemas.CardCreate],
    cards_repository: CardsRepository = FromDI(CardsRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.Cards:
    async with transaction:
        objects = await cards_repository.add_cards(deck_id, data)
        await transaction.commit()
    return schemas.Cards.from_models(objects)


@ROUTER.put("/decks/{deck_id}/cards/")
@postgres_retry
async def update_cards(
    deck_id: int,
    data: list[schemas.Card],
    cards_repository: CardsRepository = FromDI(CardsRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.Cards:
    async with transaction:
        objects = await cards_repository.upsert_cards(deck_id, data)
        await transaction.commit()
    return schemas.Cards.from_models(objects)
