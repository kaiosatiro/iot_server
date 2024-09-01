from typing import Any

import anyio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select
from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import FormValidationError
from starlette_admin.fields import HasMany, HasOne, IntegerField, TextAreaField

from src.models import Device, Site, User
from src.utils import generate_random_number


class CountingDevices(IntegerField):
    async def parse_obj(self, request: Request, obj: Site) -> int:
        session: Session = request.state.session
        stmt = select(func.count(Device.id)).where(Device.site_id == obj.id)
        count = session.execute(stmt).scalar_one()
        return count


class SiteView(ModelView):
    fields = [
        Site.id,
        Site.name,
        HasOne(
            name="user",
            label="Username",
            identity="users",
            required=True,
            searchable=True,
            exclude_from_edit=True,
        ),
        TextAreaField(
            name="description",
            label="Description",
            maxlength=255,
            exclude_from_list=True,
        ),
        CountingDevices(
            name="numberdevices",
            label="N. Devices",
            exclude_from_create=True,
            exclude_from_edit=True,
        ),
        Site.created_on,
        Site.updated_on,
        HasMany(
            name="devices",
            identity="devices",
            exclude_from_list=True,
            exclude_from_create=True,
            exclude_from_edit=True,
        ),
    ]

    exclude_fields_from_create = [Site.id, Site.created_on, Site.updated_on]
    exclude_fields_from_edit = [Site.id, Site.created_on, Site.updated_on]

    sortable_fields = [Site.name, "user", Site.created_on, Site.updated_on]
    sortable_field_mapping = {
        "user": User.username,
    }
    fields_default_sort = [(Site.updated_on, True)]

    searchable_fields = ["id", Site.name, "user"]

    async def create(self, request: Request, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data)
            session: Session | AsyncSession = request.state.session

            data["id"] = 1
            data["user_id"] = 1
            await self.validate(request, data)

            obj = await self._populate_obj(request, self.model(), data)
            obj.id = generate_random_number(1000000, 9999999)

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

    async def edit(self, request: Request, pk: Any, data: dict[str, Any]) -> Any:
        try:
            data = await self._arrange_data(request, data, True)
            session: Session | AsyncSession = request.state.session

            data["id"] = 1
            data["user_id"] = 1
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
