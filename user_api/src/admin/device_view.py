from typing import Any

import anyio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import HasOne, IntegerField, StringField, TextAreaField

from src.core.config import settings
from src.core.security import create_device_access_token
from src.models import Device, Message, Site, User
from src.utils import generate_random_number


class CountingMessages(IntegerField):
    async def parse_obj(self, request: Request, obj: Device) -> int:
        session: Session = request.state.session
        stmt = select(func.count(Message.id)).where(Message.device_id == obj.id)
        count = session.execute(stmt).scalar_one()
        return count


class UrlMessages(StringField):
    async def parse_obj(self, request: Request, obj: Device) -> str:
        return f"{settings.server_host}{settings.USERAPI_API_V1_STR}/admin/messages/list?device_id={obj.id}"


class DeviceView(ModelView):
    detail_template = "device_detail.html"
    fields = [
        Device.id,
        Device.name,
        Device.type,
        Device.model,
        Device.token,
        CountingMessages(
            name="numbermessages",
            label="N. Messages",
            exclude_from_create=True,
            exclude_from_edit=True,
            exclude_from_list=True,
        ),
        HasOne(
            name="user",
            label="Username",
            identity="users",
            required=True,
            searchable=True,
            exclude_from_edit=True,
        ),
        HasOne(
            name="site",
            label="Site",
            identity="sites",
            required=True,
            searchable=True,
        ),
        TextAreaField(
            name="description",
            label="Description",
            maxlength=255,
            exclude_from_list=True,
        ),
        Device.created_on,
        Device.updated_on,
        UrlMessages(
            name="urlmessages",
            read_only=True,
            exclude_from_list=True,
            exclude_from_create=True,
            exclude_from_edit=True,
        ),
    ]

    exclude_fields_from_list = [Device.description, Device.token]
    exclude_fields_from_create = [
        Device.token,
        Device.id,
        Device.created_on,
        Device.updated_on,
    ]
    exclude_fields_from_edit = [
        Device.token,
        Device.id,
        Device.created_on,
        Device.updated_on,
    ]

    sortable_fields = [
        Device.id,
        Device.name,
        Device.type,
        Device.model,
        "user",
        "site",
        Device.created_on,
        Device.updated_on,
    ]
    sortable_field_mapping = {
        "user": User.username,
        "site": Site.name,
    }
    fields_default_sort = [(Device.updated_on, True)]

    searchable_fields = [Device.id, Device.name, Device.type, Device.model]

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            session: Session | AsyncSession = request.state.session

            data["id"] = 1
            data["user_id"] = 1
            data["site_id"] = 1
            await self.validate(request, data)

            obj = await self._populate_obj(request, self.model(), data)
            obj.id = generate_random_number(1000000000, 2147483645)

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
            if "id" in e.orig.diag.message_detail:
                raise FormValidationError({"id": "Try again"})
            else:
                raise FormValidationError({"error": "Unknown error"})
        except Exception as e:
            return self.handle_exception(e)

    async def after_create(self, request: Request, obj: Device) -> None:
        session: Session | AsyncSession = request.state.session
        obj.token = create_device_access_token(obj.id)
        session.add(obj)
        if isinstance(session, AsyncSession):
            await session.commit()
        else:
            await anyio.to_thread.run_sync(session.commit)

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            session: Session | AsyncSession = request.state.session

            data["id"] = 1
            data["user_id"] = 1
            data["site_id"] = 1
            await self.validate(request, data)

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

    # async def repr(self, obj: Any, request: Request) -> str:
    #     return f"{obj.id}"
