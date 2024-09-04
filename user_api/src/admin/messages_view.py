from starlette.requests import Request

from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.fields import (
    HasOne,
    IntegerField,
    JSONField,
)

from src.models import Message


class MessageView(ModelView):
    # row_actions_display_type = RowActionsDisplayType.DROPDOWN
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
