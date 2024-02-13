from litestar import Litestar

from src.core.config import settings

app = Litestar(debug=settings.env.DEBUG)
