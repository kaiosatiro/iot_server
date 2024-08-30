import re
from typing import Any

import anyio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import PasswordField

from src.core.security import get_password_hash
from src.models import User
from src.utils import generate_random_number


class UserView(ModelView):
    fields = [
        User.id,
        User.username,
        User.email,
        User.about,
        User.is_active,
        User.is_superuser,
        User.created_on,
        User.updated_on,
        PasswordField(
            name="hashed_password",
            label="Password",
            required=True,
            exclude_from_list=True,
            exclude_from_detail=True,
        ),
    ]

    exclude_fields_from_list = [User.about]
    exclude_fields_from_detail = [User.hashed_password]
    exclude_fields_from_create = [
        User.id,
        User.is_active,
        User.created_on,
        User.updated_on,
    ]
    exclude_fields_from_edit = [User.created_on, User.updated_on]
    sortable_fields = [
        User.username,
        User.email,
        User.is_active,
        User.is_superuser,
        User.created_on,
        User.updated_on,
    ]
    searchable_fields = [User.id, User.username, User.email]
    fields_default_sort = [(User.username, True), (User.is_active, True)]

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        errors: dict[str, str] = dict()
        if " " in data["username"]:
            errors["username"] = "Username should not contain spaces"
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            errors["email"] = "Invalid email address"
        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            session: Session | AsyncSession = request.state.session

            data["is_active"] = True
            data["id"] = 1
            await self.validate(request, data)
            data["hashed_password"] = get_password_hash(data["hashed_password"])

            obj = await self._populate_obj(request, self.model(), data)
            obj.id = generate_random_number(10000, 99999)

            session.add(obj)
            await self.before_create(request, data, obj)
            if isinstance(session, AsyncSession):
                await session.commit()
                await session.refresh(obj)
            else:
                await anyio.to_thread.run_sync(session.commit)
                await anyio.to_thread.run_sync(session.refresh, obj)
            await self.after_create(request, obj)
            return obj
        except IntegrityError as e:
            if "email" in e.orig.diag.message_detail:
                raise FormValidationError({"email": "Email already exists"})
            elif "username" in e.orig.diag.message_detail:
                raise FormValidationError({"username": "Username already exists"})
            else:
                raise FormValidationError({"error": "Unknown error"})
        except Exception as e:
            return self.handle_exception(e)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            session: Session | AsyncSession = request.state.session

            data["id"] = 1
            await self.validate(request, data)
            data["hashed_password"] = get_password_hash(data["hashed_password"])

            obj = await self.find_by_pk(request, pk)
            await self._populate_obj(request, obj, data, True)
            session.add(obj)
            await self.before_edit(request, data, obj)
            if isinstance(session, AsyncSession):
                await session.commit()
                await session.refresh(obj)
            else:
                await anyio.to_thread.run_sync(session.commit)
                await anyio.to_thread.run_sync(session.refresh, obj)
            await self.after_edit(request, obj)
            return obj
        except IntegrityError as e:
            if "email" in e.orig.diag.message_detail:
                raise FormValidationError({"email": "Email already exists"})
            elif "username" in e.orig.diag.message_detail:
                raise FormValidationError({"username": "Username already exists"})
            else:
                raise FormValidationError({"error": "Unknown error"})
        except Exception as e:
            self.handle_exception(e)
