import os
import sys
from pathlib import Path

from litestar.__main__ import litestar_group
from litestar.__main__ import run_cli as run_litestar_cli

from src.cli.database import database_group
from src.cli.tenant import tenant_group


def run_cli():
    current_path = Path(__file__).parent.parent.parent.resolve()
    sys.path.append(str(current_path))
    os.environ.setdefault("LITESTAR_APP", "src.core.app:app")

    litestar_group.add_command(database_group)
    litestar_group.add_command(tenant_group)

    run_litestar_cli()


if __name__ == "__main__":
    run_cli()
