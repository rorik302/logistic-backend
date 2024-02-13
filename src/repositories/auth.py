from sqlalchemy import select

from src.models import Tenant, User
from src.repositories.base import BaseRepository


class TenantRepository(BaseRepository):
    async def create(self, tenant: Tenant):
        self.session.add(tenant)
        await self.session.flush()
        return tenant


class UserRepository(BaseRepository):
    async def get_or_none(self, **criteria):
        query = select(User).filter_by(**criteria)
        result = await self.session.execute(query)
        return result.scalar()

    async def create(self, user: User):
        self.session.add(user)
        await self.session.flush()
        return user
