from datetime import UTC, datetime, timedelta
from secrets import choice
from string import ascii_letters, digits
from typing import Literal
from uuid import UUID

from argon2 import PasswordHasher
from litestar import Request, status_codes
from litestar.exceptions import HTTPException

from src.core.config import settings
from src.core.database import memory_db
from src.models import Tenant, User
from src.schemas.auth import TenantCreate, Token, UserLogin
from src.services.base import BaseService


class AuthService(BaseService):
    @staticmethod
    async def _create_token(
        user: User, token_type: Literal["access", "refresh"] = "access", hash_string: str | None = None
    ):
        if token_type == "access":
            expire = int((datetime.now(UTC) + timedelta(minutes=settings.security.ACCESS_TOKEN_LIFETIME)).timestamp())
        elif token_type == "refresh":
            expire = int((datetime.now(UTC) + timedelta(minutes=settings.security.REFRESH_TOKEN_LIFETIME)).timestamp())
            hash_string = None
        else:
            raise ValueError("Недопустимое назначение токена")

        token = Token(
            user=user.id,
            tenant=user.tenant_id,
            exp=expire,
            purpose=token_type,
            hash=hash_string,
        )

        return token.encode()

    async def _create_tokens_and_cookie_string(self, user: User):
        cookie_string = "".join(choice(ascii_letters + digits) for _ in range(32))
        hash_string = PasswordHasher().hash(cookie_string)
        access_token = await self._create_token(user, hash_string=hash_string)
        refresh_token = await self._create_token(user, token_type="refresh")
        return access_token, refresh_token, cookie_string

    @staticmethod
    async def _add_tokens_to_blacklist(request: Request):
        auth_header = request.headers.get(settings.security.ACCESS_HEADER_KEY)
        if auth_header:
            auth_header_token = auth_header.split(" ")[-1]
            await memory_db.access_token_blacklist.set(
                auth_header_token, "", ex=timedelta(minutes=settings.security.ACCESS_TOKEN_LIFETIME)
            )
        refresh_cookie = request.cookies.get(settings.security.REFRESH_COOKIE_KEY)
        if refresh_cookie:
            await memory_db.refresh_token_blacklist.set(
                refresh_cookie, "", ex=timedelta(minutes=settings.security.REFRESH_TOKEN_LIFETIME)
            )

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

    async def authenticate(self, user_id: UUID = None, credentials: UserLogin = None):
        if user_id:
            user = await self.uow.user.get_or_none(id=user_id)
        elif credentials:
            user = await self.uow.user.get_or_none(email=credentials.email)
            if not user or not PasswordHasher().verify(user.password, credentials.password):
                raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)
        else:
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)

        if not user:
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            raise HTTPException("Пользователь заблокирован", status_code=status_codes.HTTP_403_FORBIDDEN)
        return user

    async def login(self, data: UserLogin, request: Request):
        async with self.uow:
            user = await self.authenticate(credentials=data)
            access_token, refresh_token, cookie_string = await self._create_tokens_and_cookie_string(user)
            await self._add_tokens_to_blacklist(request)
            return access_token, refresh_token, cookie_string

    async def refresh_token(self, request: Request):
        refresh_cookie = request.cookies.get(settings.security.REFRESH_COOKIE_KEY)
        if not refresh_cookie:
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)
        if await memory_db.refresh_token_blacklist.exists(refresh_cookie) > 0:
            raise HTTPException(status_code=status_codes.HTTP_403_FORBIDDEN)

        token = Token.decode(refresh_cookie)
        if token.purpose != "refresh":
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)

        user = await self.authenticate(user_id=token.user)
        access_token, refresh_token, cookie_string = await self._create_tokens_and_cookie_string(user)

        await self._add_tokens_to_blacklist(request)

        return access_token, refresh_token, cookie_string
