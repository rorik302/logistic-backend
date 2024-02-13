from src.core.config import settings
from src.services.base import BaseService


class DatabaseService(BaseService):
    async def create_shared_schema(self):
        async with self.uow:
            if await self.uow.database.schema_exists(settings.database.SHARED_SCHEMA_NAME):
                return

            await self.uow.database.create_schema(settings.database.SHARED_SCHEMA_NAME)
            await self.uow.database.migrate(settings.database.SHARED_SCHEMA_NAME)
