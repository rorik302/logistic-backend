from click import group

from src.core.database import async_session
from src.repositories.database import DatabaseRepository
from src.utils.decorators import run_async


@group("database")
def database_group():
    """Управление базой данных"""


@database_group.command("makemigrations")
@run_async
async def make_migrations():
    """Создание миграций"""

    schema_name = input("Schema name: ") or None
    if schema_name is None:
        raise ValueError("Нужно указать Схему")

    message = input("Message: ") or None
    if message is None:
        raise ValueError("Нужно указать 'message'")

    async with async_session() as session:
        await DatabaseRepository(session).make_migrations(schema_name, message)


@database_group.command("migrate")
@run_async
async def migrate():
    """Применение миграций"""

    schema_name = input("Schema name: ") or None
    if schema_name is None:
        raise ValueError("Нужно указать Схему")

    async with async_session() as session:
        await DatabaseRepository(session).migrate(schema_name)
