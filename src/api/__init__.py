from litestar import Router

from src.api.http.v1 import v1_router
from src.api.middlewares import JWTAuthMiddleware

api_router = Router("/api", route_handlers=[v1_router], middleware=[JWTAuthMiddleware])
