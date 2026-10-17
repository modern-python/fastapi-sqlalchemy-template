import typing

import fastapi
from modern_di_fastapi import FromDI

from app import schemas
from app.use_cases.create_deck import CreateDeckUseCase
from app.use_cases.get_deck import GetDeckUseCase
from app.use_cases.list_decks import ListDecksUseCase
from app.use_cases.update_deck import UpdateDeckUseCase


ROUTER: typing.Final = fastapi.APIRouter()


@ROUTER.get("/decks/")
async def list_decks(
    after: typing.Annotated[int | None, fastapi.Query(gt=0)] = None,
    limit: typing.Annotated[int, fastapi.Query(ge=1, le=schemas.MAX_PAGE_LIMIT)] = schemas.DEFAULT_PAGE_LIMIT,
    list_decks_use_case: ListDecksUseCase = FromDI(ListDecksUseCase),
) -> schemas.DecksPage:
    decks: typing.Final = await list_decks_use_case(after=after, limit=limit)
    return schemas.DecksPage.from_models(decks, limit=limit)


@ROUTER.get("/decks/{deck_id}/")
async def get_deck(
    deck_id: int,
    get_deck_use_case: GetDeckUseCase = FromDI(GetDeckUseCase),
) -> schemas.DeckWithCards:
    return schemas.DeckWithCards.model_validate(await get_deck_use_case(deck_id=deck_id))


@ROUTER.put("/decks/{deck_id}/")
async def update_deck(
    deck_id: int,
    data: schemas.DeckUpdate,
    update_deck_use_case: UpdateDeckUseCase = FromDI(UpdateDeckUseCase),
) -> schemas.Deck:
    return schemas.Deck.model_validate(await update_deck_use_case(deck_id=deck_id, data=data))


@ROUTER.post("/decks/")
async def create_deck(
    data: schemas.DeckCreate,
    create_deck_use_case: CreateDeckUseCase = FromDI(CreateDeckUseCase),
) -> schemas.Deck:
    return schemas.Deck.model_validate(await create_deck_use_case(data=data))
