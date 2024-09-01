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
    login_logo_url="/static/icon.svg",
    auth_provider=AdminAuthProvider(allow_paths=["/static/icon.svg"]),
    middlewares=[Middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))],
    debug=True if settings.ENVIRONMENT == "dev" else False,
)
