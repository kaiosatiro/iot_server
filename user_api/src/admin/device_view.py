from starlette_admin.contrib.sqlmodel import ModelView

from src.models import Device


class DeviceView(ModelView):
    fields = [
        Device.id,
        Device.site_id,
        Device.user_id,
        Device.name,
        Device.type,
        Device.model,
        Device.description,
        Device.created_on,
        Device.updated_on,
    ]
    exclude_fields_from_list = [Device.description, Device.token]
    exclude_fields_from_detail = [Device.token]
    exclude_fields_from_create = [Device.id, Device.created_on, Device.updated_on]
    exclude_fields_from_edit = [Device.id, Device.created_on, Device.updated_on]
    sortable_fields = [Device.name, Device.type, Device.created_on, Device.updated_on]
    searchable_fields = [Device.id, Device.name, Device.type, Device.model]
    fields_default_sort = [Device.id, (Device.created_on, True)]
