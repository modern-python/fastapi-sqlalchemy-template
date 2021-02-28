import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.db import engine
from app.deps import get_db
from app.main import app
from tests import test_data


@pytest.fixture
async def db():
    session = AsyncSession(engine)
    try:
        async with session.begin_nested():
            yield session
    except PendingRollbackError:
        pass
    finally:
        try:
            await session.rollback()
        except PendingRollbackError:
            pass
        await session.close()


@pytest.fixture
def client(db):
    def _get_db():
        return db

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def deck(db):
    instance = models.Deck(**test_data.deck.dict())
    await instance.save(db)
    return instance


@pytest.fixture
async def card(db, deck: models.Deck):
    instance = models.Card(**test_data.card.dict(), deck_id=deck.id)
    await instance.save(db)
    return instance


@pytest.fixture
async def card2(db, deck: models.Deck):
    instance = models.Card(**test_data.card2.dict(), deck_id=deck.id)
    await instance.save(db)
    return instance
