from alembic import command
from alembic.config import Config
from sqlalchemy import select, text

from src.core.config import settings
from src.repositories.base import BaseRepository


class DatabaseRepository(BaseRepository):
    async def schema_exists(self, schema_name: str):
        query = select(True).select_from(text("pg_namespace")).where(text(f"nspname = '{schema_name}'"))
        result = await self.session.execute(query)
        return result.scalar() is True

    async def create_schema(self, schema_name: str):
        query = text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        await self.session.execute(query)

    async def migrate(self, schema_name: str):
        def run_migrate(session, cfg: Config):
            cfg.attributes["session"] = session
            command.upgrade(cfg, "head")

        config = Config(settings.alembic.ini_path)
        if schema_name == settings.database.SHARED_SCHEMA_NAME:
            path = settings.alembic.shared_path
        else:
            path = settings.alembic.tenant_path
            config.attributes["schema_name"] = schema_name

        config.set_main_option("script_location", path)

        await self.session.run_sync(run_migrate, config)
