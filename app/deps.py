from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine


async def get_db():
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()
