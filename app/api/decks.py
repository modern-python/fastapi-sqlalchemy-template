import typing

import fastapi
from advanced_alchemy.exceptions import NotFoundError
from modern_di_fastapi import FromDI
from sqlalchemy import orm
from starlette import status

from app import ioc, models, schemas
from app.repositories import CardsService, DecksService


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/")
async def list_decks(
    decks_service: DecksService = FromDI(ioc.Dependencies.decks_service),
) -> schemas.Decks:
    objects = await decks_service.list()
    return typing.cast("schemas.Decks", {"items": objects})


@ROUTER.get("/decks/{deck_id}/")
async def get_deck(
    deck_id: int,
    decks_service: DecksService = FromDI(ioc.Dependencies.decks_service),
) -> schemas.Deck:
    instance = await decks_service.get_one_or_none(
        models.Deck.id == deck_id,
        load=[orm.selectinload(models.Deck.cards)],
    )
    if not instance:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck is not found")

    return typing.cast("schemas.Deck", instance)


@ROUTER.put("/decks/{deck_id}/")
async def update_deck(
    deck_id: int,
    data: schemas.DeckCreate,
    decks_service: DecksService = FromDI(ioc.Dependencies.decks_service),
) -> schemas.Deck:
    try:
        instance = await decks_service.update(data=data.model_dump(), item_id=deck_id)
    except NotFoundError:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck is not found") from None

    return typing.cast("schemas.Deck", instance)


@ROUTER.post("/decks/")
async def create_deck(
    data: schemas.DeckCreate,
    decks_service: DecksService = FromDI(ioc.Dependencies.decks_service),
) -> schemas.Deck:
    instance = await decks_service.create(data.model_dump())
    return typing.cast("schemas.Deck", instance)


@ROUTER.get("/decks/{deck_id}/cards/")
async def list_cards(
    deck_id: int,
    cards_service: CardsService = FromDI(ioc.Dependencies.cards_service),
) -> schemas.Cards:
    objects = await cards_service.list(models.Card.deck_id == deck_id)
    return typing.cast("schemas.Cards", {"items": objects})


@ROUTER.get("/cards/{card_id}/")
async def get_card(
    card_id: int,
    cards_service: CardsService = FromDI(ioc.Dependencies.cards_service),
) -> schemas.Card:
    instance = await cards_service.get_one_or_none(models.Card.id == card_id)
    if not instance:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card is not found")
    return typing.cast("schemas.Card", instance)


@ROUTER.post("/decks/{deck_id}/cards/")
async def create_cards(
    deck_id: int,
    data: list[schemas.CardCreate],
    cards_service: CardsService = FromDI(ioc.Dependencies.cards_service),
) -> schemas.Cards:
    objects = await cards_service.create_many(
        data=[models.Card(**card.model_dump(), deck_id=deck_id) for card in data],
    )
    return typing.cast("schemas.Cards", {"items": objects})


@ROUTER.put("/decks/{deck_id}/cards/")
async def update_cards(
    deck_id: int,
    data: list[schemas.Card],
    cards_service: CardsService = FromDI(ioc.Dependencies.cards_service),
) -> schemas.Cards:
    objects = await cards_service.upsert_many(
        data=[models.Card(**card.model_dump(exclude={"deck_id"}), deck_id=deck_id) for card in data],
    )
    return typing.cast("schemas.Cards", {"items": objects})
