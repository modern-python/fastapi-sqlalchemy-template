from typing import Any, List

from fastapi import APIRouter, HTTPException

from app.apps.decks import models, schemas
from app.db.utils import transaction


router = APIRouter()


@router.get("/decks/", response_model=schemas.Decks)
async def list_decks() -> Any:
    objects = await models.Deck.all()
    return {"items": objects}


@router.get("/decks/{deck_id}/", response_model=schemas.Deck)
async def get_deck(deck_id: int) -> Any:
    instance = await models.Deck.get_by_id(deck_id, prefetch=("cards",))
    if not instance:
        raise HTTPException(status_code=404, detail="Deck is not found")
    return instance


@router.put("/decks/{deck_id}/", response_model=schemas.Deck)
async def update_deck(deck_id: int, data: schemas.DeckCreate) -> Any:
    instance = await models.Deck.get_by_id(deck_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Deck is not found")
    await instance.update_attrs(**data.dict())
    await instance.save()
    return instance


@router.post("/decks/", response_model=schemas.Deck)
async def create_deck(data: schemas.DeckCreate) -> Any:
    instance = models.Deck(**data.dict())
    await instance.save()
    return instance


@router.get("/decks/{deck_id}/cards/", response_model=schemas.Cards)
async def list_cards(deck_id: int) -> Any:
    objects = await models.Card.filter({"deck_id": deck_id})
    return {"items": objects}


@router.get("/cards/{card_id}/", response_model=schemas.Card)
async def get_card(card_id: int) -> Any:
    instance = await models.Card.get_by_id(card_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Card is not found")
    return instance


@router.post("/decks/{deck_id}/cards/", response_model=schemas.Cards)
async def create_cards(deck_id: int, data: List[schemas.CardCreate]) -> Any:
    async with transaction():
        objects = await models.Card.bulk_create(
            [models.Card(**card.dict(), deck_id=deck_id) for card in data],
        )
    return {"items": objects}


@router.put("/decks/{deck_id}/cards/", response_model=schemas.Cards)
async def update_cards(deck_id: int, data: List[schemas.Card]) -> Any:
    async with transaction():
        objects = await models.Card.bulk_update(
            [models.Card(**card.dict(exclude={"deck_id"}), deck_id=deck_id) for card in data],
        )
    return {"items": objects}
