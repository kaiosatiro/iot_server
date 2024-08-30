from starlette_admin.contrib.sqlmodel import Admin
# from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware

from src.core.config import settings
from src.core.db import engine
from src.admin.login import AuthProvider

admin = Admin(
    engine=engine,
    base_url="/admin",
    route_name="Admin",
    title="IoT Server Admin Panel",
    # logo_url="`https`://preview.tabler.io/static/logo-white.svg",
    # login_logo_url="`https`://preview.tabler.io/static/logo.svg",
    # login_logo_url="/admin/statics/logo.svg",  # base_url + '/statics/' + path_to_the_file
    # auth_provider=AuthProvider(allow_paths=["/statics/logo.svg"]),
    # middlewares=[Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)],
    debug=True if settings.ENVIRONMENT == "dev" else False,
)
