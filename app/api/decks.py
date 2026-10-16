import typing

import fastapi
from db_retry import Transaction, postgres_retry
from modern_di_fastapi import FromDI

from app import schemas
from app.repositories import DecksRepository


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/")
@postgres_retry
async def list_decks(
    decks_repository: DecksRepository = FromDI(DecksRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.Decks:
    async with transaction:
        objects = await decks_repository.get_many()
        await transaction.commit()
    return schemas.Decks.from_models(objects)


@ROUTER.get("/decks/{deck_id}/")
@postgres_retry
async def get_deck(
    deck_id: int,
    decks_repository: DecksRepository = FromDI(DecksRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.DeckWithCards:
    async with transaction:
        instance = await decks_repository.fetch_with_cards(deck_id)
        await transaction.commit()
    return schemas.DeckWithCards.model_validate(instance)


@ROUTER.put("/decks/{deck_id}/")
@postgres_retry
async def update_deck(
    deck_id: int,
    data: schemas.DeckCreate,
    decks_repository: DecksRepository = FromDI(DecksRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.Deck:
    async with transaction:
        instance = await decks_repository.update(data=data.model_dump(), item_id=deck_id)
        await transaction.commit()
    return schemas.Deck.model_validate(instance)


@ROUTER.post("/decks/")
@postgres_retry
async def create_deck(
    data: schemas.DeckCreate,
    decks_repository: DecksRepository = FromDI(DecksRepository),
    transaction: Transaction = FromDI(Transaction),
) -> schemas.Deck:
    async with transaction:
        instance = await decks_repository.create(data.model_dump())
        await transaction.commit()
    return schemas.Deck.model_validate(instance)
