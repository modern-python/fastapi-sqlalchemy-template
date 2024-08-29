from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app import models, schemas


class DeckModelFactory(SQLAlchemyFactory[models.Deck]):
    __model__ = models.Deck
    id = None


class CardModelFactory(SQLAlchemyFactory[models.Card]):
    __model__ = models.Card
    id = None


class CardCreateSchemaFactory(ModelFactory[schemas.CardCreate]):
    __model__ = schemas.CardCreate
