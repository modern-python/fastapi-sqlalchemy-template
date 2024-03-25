from sqlalchemy.ext import asyncio as sa_async
from that_depends import BaseContainer, providers

from app.db.resource import create_sa_engine
from app.db.session import Session
from app.repositories.decks import CardsRepository, DecksRepository


class IOCContainer(BaseContainer):
    database_engine = providers.AsyncResource[sa_async.AsyncEngine](create_sa_engine)
    session = providers.Factory(Session.get)

    decks_repo = providers.Factory(DecksRepository, session=session)
    cards_repo = providers.Factory(CardsRepository, session=session)
