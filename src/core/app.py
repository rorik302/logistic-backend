from litestar import Litestar

from src.api import api_router
from src.core.config import settings
from src.utils.database import init_shared_schema

app = Litestar(debug=settings.env.DEBUG, on_startup=[init_shared_schema], route_handlers=[api_router])
