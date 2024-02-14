from litestar import Router

from src.api.http.v1.auth import AuthController

v1_router = Router("/v1", route_handlers=[AuthController])
