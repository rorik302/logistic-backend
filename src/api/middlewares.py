from argon2 import PasswordHasher
from litestar import status_codes
from litestar.connection import ASGIConnection
from litestar.exceptions import HTTPException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult
from litestar.types import ASGIApp

from src.core.config import settings
from src.core.database import async_session
from src.core.unit_of_work import UnitOfWork
from src.schemas.auth import Token


class JWTAuthMiddleware(AbstractAuthenticationMiddleware):
    exclude = ["/api/v1/auth/login", "/api/v1/auth/refresh"]

    def __init__(self, app: ASGIApp):
        super().__init__(app, exclude=self.exclude)

    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        auth_header = connection.headers.get(settings.security.ACCESS_HEADER_KEY)
        if not auth_header:
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)

        encoded_token = auth_header.split(" ")[-1]
        token = Token.decode(encoded_token)

        if token.purpose != "access":
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)

        cookie_string = connection.cookies.get(settings.security.COOKIE_STRING_KEY)
        if not PasswordHasher().verify(token.hash, cookie_string):
            raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)

        async with async_session() as session, UnitOfWork(session) as uow:
            user = await uow.user.get_or_none(id=token.user)
            if not user:
                raise HTTPException(status_code=status_codes.HTTP_401_UNAUTHORIZED)
            if not user.is_active:
                raise HTTPException("Пользователь заблокирован")

        return AuthenticationResult(user, encoded_token)
