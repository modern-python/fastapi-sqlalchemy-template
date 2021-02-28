from sqlalchemy.exc import PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine


async def get_db():
    session = AsyncSession(engine)
    try:
        async with session.begin_nested():
            yield session
    except PendingRollbackError:
        pass
    finally:
        try:
            await session.commit()
        except PendingRollbackError:
            pass
        await session.close()
