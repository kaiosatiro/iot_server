from collections.abc import Sequence
from typing import Any
from urllib.parse import parse_qs, urlparse

import anyio
import anyio.to_thread
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Session,
    joinedload,
)
from starlette.requests import Request
from starlette_admin._types import RequestAction
from starlette_admin.contrib.sqla.helpers import (
    build_query,
)
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.fields import (
    HasOne,
    IntegerField,
    JSONField,
    RelationField,
)

from src.models import Message


class MessageView(ModelView):
    list_template = "message_list.html"
    detail_template = "message_detail.html"
    fields = [
        IntegerField(
            name="id",
            label="ID",
            read_only=True,
            searchable=True,
            exclude_from_list=True,
        ),
        Message.inserted_on,
        HasOne(
            name="device",
            label="Device",
            identity="devices",
            read_only=True,
            searchable=True,
            exclude_from_list=True,
            exclude_from_edit=True,
        ),
        IntegerField(
            name="device_id",
            label="Device ID",
            read_only=True,
            searchable=True,
        ),
        JSONField(
            name="message",
            label="Message",
            read_only=True,
            orderable=False,
            height="30em",
        ),
    ]

    exclude_fields_from_edit = [Message.inserted_on]
    exclude_fields_from_detail = [Message.inserted_on]
    sortable_fields = [Message.inserted_on, Message.device_id]
    fields_default_sort = [(Message.inserted_on, True)]

    searchable_fields = [Message.inserted_on, Message.device_id]

    def is_accessible(self, request: Request) -> bool:
        return True

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    async def find_all(  # noqa: C901
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: dict[str, Any] | str | None = None,
        order_by: list[str] | None = None,
    ) -> Sequence[Any]:
        # Workaround for my custom query WHERE clause
        try:
            url = request.headers._list[7][1]
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            where_value = int(query_params.get(b"where", [""])[0])
        except ValueError:
            where_value = None
        except IndexError:
            where_value = None
        except TypeError:
            where_value = None
        # -------------------------------------------

        session: Session | AsyncSession = request.state.session
        stmt = self.get_list_query().offset(skip)
        if limit > 0:
            stmt = stmt.limit(limit)
        if where is not None:
            if isinstance(where, dict):
                where = build_query(where, self.model)
            else:
                where = await self.build_full_text_search_query(
                    request, where, self.model
                )
            stmt = stmt.where(where)  # type: ignore
        if where_value:
            stmt = stmt.where(self.model.device_id == where_value)
        stmt = self.build_order_clauses(request, order_by or [], stmt)
        for field in self.get_fields_list(request, RequestAction.LIST):
            if isinstance(field, RelationField):
                stmt = stmt.options(joinedload(getattr(self.model, field.name)))
        if isinstance(session, AsyncSession):
            return (await session.execute(stmt)).scalars().unique().all()
        return (
            (await anyio.to_thread.run_sync(session.execute, stmt))
            .scalars()
            .unique()
            .all()
        )
