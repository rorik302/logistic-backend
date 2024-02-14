from datetime import UTC, datetime, timedelta
from secrets import choice
from string import ascii_letters, digits

from argon2 import PasswordHasher
from litestar.exceptions import HTTPException

from src.core.config import settings
from src.models import Tenant, User
from src.schemas.auth import TenantCreate, Token, UserLogin
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

    async def login(self, data: UserLogin):
        async with self.uow:
            login_exception = HTTPException("Неверная почта или пароль")
            user = await self.uow.user.get_or_none(email=data.email)
            if not user:
                raise login_exception
            if not PasswordHasher().verify(user.password, data.password):
                raise login_exception
            if not user.is_active:
                raise HTTPException("Пользователь заблокирован")

            cookie_string = "".join(choice(ascii_letters + digits) for _ in range(32))
            hash_string = PasswordHasher().hash(cookie_string)

            access_token = Token(
                user=user.id,
                tenant=user.tenant_id,
                exp=int((datetime.now(UTC) + timedelta(minutes=settings.security.ACCESS_TOKEN_LIFETIME)).timestamp()),
                purpose="access",
                hash=hash_string,
            ).encode()

            refresh_token = Token(
                user=user.id,
                tenant=user.tenant_id,
                exp=int((datetime.now(UTC) + timedelta(minutes=settings.security.REFRESH_TOKEN_LIFETIME)).timestamp()),
                purpose="refresh",
            ).encode()

            return access_token, refresh_token, cookie_string
