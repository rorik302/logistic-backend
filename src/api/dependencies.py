from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session
from src.core.unit_of_work import UnitOfWork


async def provide_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def provide_unit_of_work(session: AsyncSession) -> UnitOfWork:
    # session берётся из dependency injection
    return UnitOfWork(session)
