from click import group

from src.core.database import async_session
from src.core.unit_of_work import UnitOfWork
from src.schemas.auth import TenantCreate
from src.services.auth import AuthService
from src.utils.decorators import run_async


@group("tenant")
def tenant_group():
    """Управление тенантами"""


@tenant_group.command("create")
@run_async
async def register_tenant():
    """Создание тенанта"""

    email = input("Email: ")
    password = input("Password: ")
    schema_name = input("Schema name: ") or None

    async with async_session() as session, UnitOfWork(session) as uow:
        await AuthService(uow).register_tenant(TenantCreate(email=email, password=password, schema_name=schema_name))
