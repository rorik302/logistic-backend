from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import settings

async_engine = create_async_engine(settings.database.DB_URL, echo=settings.env.DEBUG, pool_pre_ping=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False, autocommit=False)

metadata = MetaData()
shared_metadata = MetaData(schema=settings.database.SHARED_SCHEMA_NAME)
