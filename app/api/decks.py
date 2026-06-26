import typing

import fastapi
from modern_di_fastapi import FromDI

from app import schemas
from app.repositories import DecksRepository


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/")
async def list_decks(
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.Decks:
    objects = await decks_repository.get_many()
    return schemas.Decks.from_models(objects)


@ROUTER.get("/decks/{deck_id}/")
async def get_deck(
    deck_id: int,
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.DeckWithCards:
    instance = await decks_repository.fetch_with_cards(deck_id)
    return schemas.DeckWithCards.model_validate(instance)


@ROUTER.put("/decks/{deck_id}/")
async def update_deck(
    deck_id: int,
    data: schemas.DeckCreate,
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.Deck:
    instance = await decks_repository.update(data=data.model_dump(), item_id=deck_id)
    return schemas.Deck.model_validate(instance)


@ROUTER.post("/decks/")
async def create_deck(
    data: schemas.DeckCreate,
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.Deck:
    instance = await decks_repository.create(data.model_dump())
    return schemas.Deck.model_validate(instance)
