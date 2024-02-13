from os import getenv
from pathlib import Path
from typing import Literal, get_args, get_origin

from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = Path(__file__).parent.parent.parent


def cast_bool(value: str) -> bool:
    if value.lower() in ["false", "0"]:
        return False
    elif value.lower() in ["true", "1"]:
        return True


class BaseSettings:

    def __init__(self):
        self.validate()

    def validate(self):
        errors = {}

        for field in self.__annotations__:
            if not field.isupper():
                continue

            field_value = getattr(self, field)
            var_type = self.__annotations__[field]

            # Валидация Literal
            if get_origin(var_type) == Literal:
                if field_value not in get_args(var_type):
                    errors[field] = f"Значение {field} должно быть одним из {get_args(var_type)}"
            # Валидация остальных типов
            else:
                if var_type == bool:
                    value = cast_bool(field_value)
                    if not isinstance(value, bool):
                        errors[field] = f"Значение {field} должно иметь тип {bool}, а имеет тип {type(field_value)}"
                else:
                    value = var_type(field_value)
                self.__setattr__(field, value)

            if len(errors) > 0:
                raise ValueError(errors)


class AlembicSettings(BaseSettings):
    ini_path: str = (PROJECT_DIR / "alembic.ini").as_posix()
    shared_path: str = (PROJECT_DIR / "src/migrations/shared").as_posix()
    tenant_path: str = (PROJECT_DIR / "src/migrations/tenant").as_posix()


class DatabaseSettings(BaseSettings):
    DB_NAME: str = getenv("DB_NAME")
    DB_USER: str = getenv("DB_USER")
    DB_PASSWORD: str = getenv("DB_PASSWORD")
    DB_HOST: str = getenv("DB_HOST")
    DB_PORT: int = int(getenv("DB_PORT"))

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    SHARED_SCHEMA_NAME: str = "shared"


class EnvSettings(BaseSettings):
    MODE: Literal["DEV", "PROD"] = getenv("MODE")
    DEBUG: bool = getenv("DEBUG") or MODE != "PROD"
    RELOAD: bool = getenv("RELOAD") or DEBUG


class SecuritySettings(BaseSettings):
    SSL_KEYFILE: str = PROJECT_DIR / "certs" / "key.pem"
    SSL_CERTFILE: str = PROJECT_DIR / "certs" / "cert.pem"


class Settings:
    alembic: AlembicSettings = AlembicSettings()
    database: DatabaseSettings = DatabaseSettings()
    env: EnvSettings = EnvSettings()
    security: SecuritySettings = SecuritySettings()


settings: Settings = Settings()
