import pytest
from alembic.config import main
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db import engine
from app.main import app
from tests import test_data


@pytest.fixture
def client():
    main(["--raiseerr", "downgrade", "base"])
    main(["--raiseerr", "upgrade", "head"])

    with TestClient(app) as client:
        yield client

    main(["--raiseerr", "downgrade", "base"])


@pytest.fixture
async def db(client):
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
async def deck(db):
    instance = models.Deck(**test_data.deck.dict())
    await instance.save(db)
    return instance


@pytest.fixture
async def deck2(db):
    instance = models.Deck(**test_data.deck2.dict())
    await instance.save(db)
    return instance
