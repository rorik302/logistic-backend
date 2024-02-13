from uuid import uuid4


def generate_tenant_schema_name():
    return f"tenant_{str(uuid4()).replace('-', '_')}"
