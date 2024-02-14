from typing import Literal
from uuid import UUID

import jwt
from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from jwt import ExpiredSignatureError
from litestar import status_codes
from litestar.dto import DTOConfig
from litestar.exceptions import HTTPException
from pydantic import EmailStr

from src.core.config import settings
from src.models import User
from src.schemas.base import BaseSchema


class TenantCreate(BaseSchema):
    email: EmailStr
    password: str
    schema_name: str


class UserLogin(BaseSchema):
    email: EmailStr
    password: str


class UserReturnDTO(SQLAlchemyDTO[User]):
    config = DTOConfig(exclude={"password", "tenant"})


class Token(BaseSchema):
    user: UUID
    tenant: UUID
    exp: int
    purpose: Literal["access", "refresh"]
    hash: str | None = None

    def encode(self):
        return jwt.encode(self.model_dump(mode="json"), settings.security.PRIVATE_KEY, settings.security.ALGORITHM)

    @classmethod
    def decode(cls, encoded_token: str):
        try:
            return cls(
                **jwt.decode(encoded_token, settings.security.PUBLIC_KEY, algorithms=[settings.security.ALGORITHM])
            )
        except ExpiredSignatureError as exc:
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED) from exc
