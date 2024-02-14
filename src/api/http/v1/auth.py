from litestar import Response, post, status_codes
from litestar.di import Provide

from src.api.base import BaseController
from src.api.dependencies import provide_session, provide_unit_of_work
from src.core.config import settings
from src.core.unit_of_work import UnitOfWork
from src.schemas.auth import UserLogin
from src.services.auth import AuthService


class AuthController(BaseController):
    path = "/auth"
    tags = ["Auth"]
    dependencies = {"session": Provide(provide_session), "uow": Provide(provide_unit_of_work)}

    @post("/login")
    async def login(self, uow: UnitOfWork, data: UserLogin) -> Response[None]:
        access_token, refresh_token, cookie_string = await AuthService(uow).login(data)
        response = Response(None, status_code=status_codes.HTTP_200_OK)
        response.headers["Authorization"] = f"Bearer {access_token}"
        response.set_cookie(
            settings.security.REFRESH_COOKIE_KEY,
            refresh_token,
            settings.security.REFRESH_TOKEN_LIFETIME,
            secure=True,
            httponly=True,
        )
        response.set_cookie(
            settings.security.COOKIE_STRING_KEY,
            cookie_string,
            settings.security.ACCESS_TOKEN_LIFETIME,
            secure=True,
            httponly=True,
        )
        return response
