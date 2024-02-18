from litestar import Litestar
from litestar.config.cors import CORSConfig

from src.api import api_router
from src.core.config import settings
from src.utils.database import init_shared_schema

cors_config = CORSConfig(
    allow_origins=settings.security.CORS_ALLOW_ORIGINS,
    allow_origin_regex=settings.security.CORS_ALLOW_ORIGINS_REGEX,
    allow_credentials=True,
    expose_headers=["Authorization"],
)

app = Litestar(
    debug=settings.env.DEBUG, on_startup=[init_shared_schema], route_handlers=[api_router], cors_config=cors_config
)
