from typing import Literal
from uuid import UUID

import jwt
from pydantic import EmailStr

from src.core.config import settings
from src.schemas.base import BaseSchema


class TenantCreate(BaseSchema):
    email: EmailStr
    password: str
    schema_name: str


class UserLogin(BaseSchema):
    email: EmailStr
    password: str


class Token(BaseSchema):
    user: UUID
    tenant: UUID
    exp: int
    purpose: Literal["access", "refresh"]
    hash: str | None = None

    def encode(self):
        return jwt.encode(self.model_dump(mode="json"), settings.security.PRIVATE_KEY, settings.security.ALGORITHM)
