from litestar import Litestar

from src.core.config import settings
from src.utils.database import init_shared_schema

app = Litestar(debug=settings.env.DEBUG, on_startup=[init_shared_schema])
