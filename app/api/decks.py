import typing

import fastapi
from modern_di_fastapi import FromDI

from app import models, schemas
from app.repositories import CardsRepository, DecksRepository


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/")
async def list_decks(
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.Decks:
    objects = await decks_repository.get_many()
    return typing.cast("schemas.Decks", {"items": objects})


@ROUTER.get("/decks/{deck_id}/")
async def get_deck(
    deck_id: int,
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.Deck:
    instance = await decks_repository.fetch_with_cards(deck_id)
    return typing.cast("schemas.Deck", instance)


@ROUTER.put("/decks/{deck_id}/")
async def update_deck(
    deck_id: int,
    data: schemas.DeckCreate,
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.Deck:
    instance = await decks_repository.update(data=data.model_dump(), item_id=deck_id)
    return typing.cast("schemas.Deck", instance)


@ROUTER.post("/decks/")
async def create_deck(
    data: schemas.DeckCreate,
    decks_repository: DecksRepository = FromDI(DecksRepository),
) -> schemas.Deck:
    instance = await decks_repository.create(data.model_dump())
    return typing.cast("schemas.Deck", instance)


@ROUTER.get("/decks/{deck_id}/cards/")
async def list_cards(
    deck_id: int,
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Cards:
    objects = await cards_repository.list_for_deck(deck_id)
    return typing.cast("schemas.Cards", {"items": objects})


@ROUTER.get("/cards/{card_id}/")
async def get_card(
    card_id: int,
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Card:
    instance = await cards_repository.get_one(models.Card.id == card_id)
    return typing.cast("schemas.Card", instance)


@ROUTER.post("/decks/{deck_id}/cards/")
async def create_cards(
    deck_id: int,
    data: list[schemas.CardCreate],
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Cards:
    objects = await cards_repository.add_cards(deck_id, data)
    return typing.cast("schemas.Cards", {"items": objects})


@ROUTER.put("/decks/{deck_id}/cards/")
async def update_cards(
    deck_id: int,
    data: list[schemas.Card],
    cards_repository: CardsRepository = FromDI(CardsRepository),
) -> schemas.Cards:
    objects = await cards_repository.upsert_cards(deck_id, data)
    return typing.cast("schemas.Cards", {"items": objects})
