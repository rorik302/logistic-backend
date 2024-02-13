from datetime import datetime
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import expression

from src.core.database import metadata


class BaseModel(DeclarativeBase):
    metadata = metadata

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(server_default=text("now()"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=text("now()"), onupdate=text("now()"), nullable=False)
    is_active: Mapped[bool] = mapped_column(server_default=expression.true(), nullable=False)
