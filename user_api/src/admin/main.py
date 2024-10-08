import secrets

from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqlmodel import Admin

from src.admin.login import AdminAuthProvider
from src.core.config import settings
from src.core.db import engine

admin = Admin(
    engine=engine,
    base_url="/admin",
    route_name="Admin",
    title="IoT Server Admin Panel",
    templates_dir="src/admin/templates",  # TODO: change to settings?
    statics_dir="src/admin/statics",  # TODO: change to settings?
    login_logo_url=f"{settings.USERAPI_API_V1_STR}/static/icon.ico",
    logo_url=f"{settings.USERAPI_API_V1_STR}/static/icon.ico",
    favicon_url=f"{settings.USERAPI_API_V1_STR}/favicon.ico",
    auth_provider=AdminAuthProvider(
        allow_paths=[f"{settings.USERAPI_API_V1_STR}/static/icon.svg"]
    ),
    middlewares=[Middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))],
    debug=True if settings.ENVIRONMENT == "dev" else False,
)
