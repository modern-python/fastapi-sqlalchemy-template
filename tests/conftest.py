import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.db import engine
from app.deps import get_db
from app.main import app
from tests import test_data


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db():
    # joining session into external transaction
    # https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


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
