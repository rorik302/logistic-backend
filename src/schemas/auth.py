from pydantic import EmailStr

from src.schemas.base import BaseSchema


class TenantCreate(BaseSchema):
    email: EmailStr
    password: str
    schema_name: str
