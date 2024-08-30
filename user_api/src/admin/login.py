from fastapi import Request, Response
from sqlmodel import Session, select
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from src.core.db import engine
from src.core.security import verify_password
from src.models import User


class AdminAuthProvider(AuthProvider):
    session: Session = Session(engine)

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 1:
            raise FormValidationError({"username": "Ensure username is not empty"})
        if len(password) < 1:
            raise FormValidationError({"password": "Ensure password is not empty"})

        with self.session as db:
            statement = select(User).where(User.username == username)
            user = db.exec(statement).first()

        if not user:
            # logger.warning("User %s failed to authenticate", form_data.username)
            raise LoginFailed("Invalid username or password")
        if not verify_password(password, user.hashed_password):
            raise LoginFailed("Invalid username or password")

        if not user.is_active or not user.is_superuser:
            # logger.warning("User %s is inactive", form_data.username)
            raise LoginFailed("Unauthorized")

        request.session.update({"username": username})
        return response

    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("username", None):
            with self.session as db:
                statement = select(User).where(
                    User.username == request.session.get("username", None)
                )
                user = db.exec(statement).first()
            request.state.user = user.username
            return True
        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user = request.state.user
        custom_app_title = "Hello, " + user + "!"
        return AdminConfig(
            app_title=custom_app_title,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        return AdminUser(username=user)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
