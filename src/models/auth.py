from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import shared_metadata
from src.models.base import BaseModel
from src.utils.helpers import generate_tenant_schema_name


class Tenant(BaseModel):
    __tablename__ = "tenants"
    metadata = shared_metadata

    schema_name: Mapped[str] = mapped_column(unique=True, default=generate_tenant_schema_name, nullable=False)
    users: Mapped[list["User"]] = relationship("User", back_populates="tenant")


class User(BaseModel):
    __tablename__ = "users"
    metadata = shared_metadata

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
