from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.auth import TenantRepository, UserRepository
from src.repositories.database import DatabaseRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

        self.database: DatabaseRepository = DatabaseRepository(self.session)
        self.tenant: TenantRepository = TenantRepository(self.session)
        self.user: UserRepository = UserRepository(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
