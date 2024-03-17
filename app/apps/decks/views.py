import typing

import fastapi

from app.apps.decks import models, schemas
from app.db.utils import transaction


router = fastapi.APIRouter()


@router.get("/decks/")
async def list_decks() -> schemas.Decks:
    objects = await models.Deck.all()
    return typing.cast(schemas.Decks, {"items": objects})


@router.get("/decks/{deck_id}/")
async def get_deck(deck_id: int) -> schemas.Deck:
    instance = await models.Deck.get_by_id(deck_id, prefetch=("cards",))
    if not instance:
        raise fastapi.HTTPException(status_code=404, detail="Deck is not found")
    return typing.cast(schemas.Deck, instance)


@router.put("/decks/{deck_id}/")
async def update_deck(deck_id: int, data: schemas.DeckCreate) -> schemas.Deck:
    instance = await models.Deck.get_by_id(deck_id)
    if not instance:
        raise fastapi.HTTPException(status_code=404, detail="Deck is not found")
    await instance.update_attrs(**data.dict())
    await instance.save()
    return typing.cast(schemas.Deck, instance)


@router.post("/decks/")
async def create_deck(data: schemas.DeckCreate) -> schemas.Deck:
    instance = models.Deck(**data.dict())
    await instance.save()
    return typing.cast(schemas.Deck, instance)


@router.get("/decks/{deck_id}/cards/")
async def list_cards(deck_id: int) -> schemas.Cards:
    objects = await models.Card.filter({"deck_id": deck_id})
    return typing.cast(schemas.Cards, {"items": objects})


@router.get("/cards/{card_id}/")
async def get_card(card_id: int) -> schemas.Card:
    instance = await models.Card.get_by_id(card_id)
    if not instance:
        raise fastapi.HTTPException(status_code=404, detail="Card is not found")
    return typing.cast(schemas.Card, instance)


@router.post("/decks/{deck_id}/cards/")
async def create_cards(deck_id: int, data: list[schemas.CardCreate]) -> schemas.Cards:
    async with transaction():
        objects = await models.Card.bulk_create(
            [models.Card(**card.dict(), deck_id=deck_id) for card in data],
        )
    return typing.cast(schemas.Cards, {"items": objects})


@router.put("/decks/{deck_id}/cards/")
async def update_cards(deck_id: int, data: list[schemas.Card]) -> schemas.Cards:
    async with transaction():
        objects = await models.Card.bulk_update(
            [models.Card(**card.dict(exclude={"deck_id"}), deck_id=deck_id) for card in data],
        )
    return typing.cast(schemas.Cards, {"items": objects})
