from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import RequestValidationError
from pydantic import parse_obj_as
from pydantic.error_wrappers import ErrorWrapper
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db import DatabaseValidationError, ObjectDoesNotExist
from app.deps import get_db


router = APIRouter()


@router.get("/decks/", response_model=schemas.Decks)
async def list_decks(db: AsyncSession = Depends(get_db)):
    objects = await models.Deck.all(db)
    return schemas.Decks(decks=parse_obj_as(List[schemas.Deck], objects))


@router.get("/decks/{deck_id}/", response_model=schemas.Deck)
async def get_deck(deck_id: int, db: AsyncSession = Depends(get_db)):
    try:
        instance = await models.Deck.get_by_id(db, deck_id)
    except ObjectDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return schemas.Deck.from_orm(instance)


@router.patch("/decks/{deck_id}/", response_model=schemas.Deck)
async def update_deck(
    deck_id: int, data: schemas.Deck, db: AsyncSession = Depends(get_db)
):
    try:
        instance = await models.Deck.get_by_id(db, deck_id)
    except ObjectDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    try:
        await instance.update(
            db, **data.dict(exclude_unset=True, exclude={"id"})
        )
    except DatabaseValidationError as e:
        raise RequestValidationError(
            [
                ErrorWrapper(
                    ValueError(e.message), ["body", e.field or "__root__"]
                )
            ]
        )
    return schemas.Deck.from_orm(instance)


@router.post("/decks/", response_model=schemas.Deck)
async def create_deck(data: schemas.Deck, db: AsyncSession = Depends(get_db)):
    instance = models.Deck(**data.dict(exclude={"id"}))
    try:
        await instance.save(db)
    except DatabaseValidationError as e:
        raise RequestValidationError(
            [
                ErrorWrapper(
                    ValueError(e.message), ["body", e.field or "__root__"]
                )
            ]
        )
    return schemas.Deck.from_orm(instance)
