import typing

import fastapi
from modern_di_fastapi import FromDI

from app import schemas
from app.use_cases.create_cards import CreateCardsUseCase
from app.use_cases.get_card import GetCardUseCase
from app.use_cases.list_cards import ListCardsUseCase
from app.use_cases.update_cards import UpdateCardsUseCase


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/{deck_id}/cards/")
async def list_cards(
    deck_id: int,
    list_cards_use_case: ListCardsUseCase = FromDI(ListCardsUseCase),
) -> schemas.Cards:
    return schemas.Cards.from_models(await list_cards_use_case(deck_id=deck_id))


@ROUTER.get("/cards/{card_id}/")
async def get_card(
    card_id: int,
    get_card_use_case: GetCardUseCase = FromDI(GetCardUseCase),
) -> schemas.Card:
    return schemas.Card.model_validate(await get_card_use_case(card_id=card_id))


@ROUTER.post("/decks/{deck_id}/cards/")
async def create_cards(
    deck_id: int,
    data: list[schemas.CardCreate],
    create_cards_use_case: CreateCardsUseCase = FromDI(CreateCardsUseCase),
) -> schemas.Cards:
    return schemas.Cards.from_models(await create_cards_use_case(deck_id=deck_id, data=data))


@ROUTER.put("/decks/{deck_id}/cards/")
async def update_cards(
    deck_id: int,
    data: list[schemas.Card],
    update_cards_use_case: UpdateCardsUseCase = FromDI(UpdateCardsUseCase),
) -> schemas.Cards:
    return schemas.Cards.from_models(await update_cards_use_case(deck_id=deck_id, data=data))
