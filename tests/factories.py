from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app import models, schemas


class DeckModelFactory(SQLAlchemyFactory[models.Deck]):
    __set_association_proxy__ = False
    __set_relationships__ = False
    __check_model__ = False
    id = None


class CardModelFactory(SQLAlchemyFactory[models.Card]):
    __set_association_proxy__ = False
    __set_relationships__ = False
    __check_model__ = False
    id = None


class CardCreateSchemaFactory(ModelFactory[schemas.CardCreate]):
    __set_association_proxy__ = False
    __set_relationships__ = False
    __check_model__ = False
