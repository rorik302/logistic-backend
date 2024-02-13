import asyncio
from logging.config import fileConfig

from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, engine_from_config, pool, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import metadata
from src.models import tenant_models  # noqa

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata

config.set_main_option("sqlalchemy.url", settings.database.DB_URL)

schema_name = config.attributes.get("schema_name") or context.get_x_argument(as_dictionary=True).get("schema_name")
if schema_name is None:
    raise ValueError("Не указана схема")


def include_object(object_, name, type_, reflected, compare_to):
    if type_ == "foreign_key_constraint":
        return False

    return True


def process_revision_directives(context_, revision, directives):
    if config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []

        head_revision = ScriptDirectory.from_config(context.config).get_current_head()

        if head_revision is None:
            new_rev_id = 1
        else:
            last_rev_id = int(head_revision.lstrip("0"))
            new_rev_id = last_rev_id + 1
        script.rev_id = f"{new_rev_id:04}"


def do_run_migrations(connection: Connection) -> None:
    connection.execute(text(f"SET search_path TO {schema_name}"))
    connection.commit()
    connection.dialect.default_schema_name = schema_name

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations(connectable) -> None:
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    connectable: Session | AsyncEngine = config.attributes.get("session")

    if connectable is None:
        connectable = AsyncEngine(
            engine_from_config(
                context.config.get_section(context.config.config_ini_section),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
                future=True,
            )
        )

    if isinstance(connectable, AsyncEngine):
        asyncio.run(run_async_migrations(connectable))
    else:
        do_run_migrations(connectable.connection())


run_migrations_online()
