from src.core.database import async_session
from src.core.unit_of_work import UnitOfWork
from src.services.database import DatabaseService


async def init_shared_schema():
    async with async_session() as session, UnitOfWork(session) as uow:
        await DatabaseService(uow).create_shared_schema()
