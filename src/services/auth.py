from argon2 import PasswordHasher

from src.models import Tenant, User
from src.schemas.auth import TenantCreate
from src.services.base import BaseService


class AuthService(BaseService):
    async def register_tenant(self, data: TenantCreate):
        async with self.uow:
            schema_exists = await self.uow.database.schema_exists(data.schema_name)
            if schema_exists:
                raise ValueError(f"Схема {data.schema_name} уже занята")
            db_user = await self.uow.user.get_or_none(email=data.email)
            if db_user:
                raise ValueError(f"Пользователь с почтой {data.email} уже существует")

            tenant_instance = Tenant(schema_name=data.schema_name) if data.schema_name else Tenant()
            tenant = await self.uow.tenant.create(tenant_instance)
            user_instance = User(email=data.email, password=PasswordHasher().hash(data.password), tenant_id=tenant.id)
            await self.uow.user.create(user_instance)

            # commit происходит в migrate
            await self.uow.database.create_schema(tenant.schema_name)
            await self.uow.database.migrate(tenant.schema_name)
