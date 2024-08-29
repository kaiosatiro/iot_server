from starlette_admin.contrib.sqlmodel import Admin, ModelView
from starlette_admin.views import DropDown, Link

from src.core.config import settings
from src.core.db import engine
from src.models import Device, Site, User

admin = Admin(
    engine=engine,
    base_url="/admin",
    route_name="Admin",
    title="IoT Server Admin Panel",
    # logo_url="`https`://preview.tabler.io/static/logo-white.svg",
    # login_logo_url="`https`://preview.tabler.io/static/logo.svg",
    debug=True if settings.ENVIRONMENT == "dev" else False,
)


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
    ]
    exclude_fields_from_list = [User.about]
    exclude_fields_from_detail = [User.hashed_password]
    exclude_fields_from_create = [User.id, User.created_on, User.updated_on]
    exclude_fields_from_edit = [User.id, User.created_on, User.updated_on]
    sortable_fields = [
        User.username,
        User.email,
        User.is_active,
        User.is_superuser,
        User.created_on,
        User.updated_on,
    ]
    searchable_fields = [User.id, User.username, User.email]
    fields_default_sort = [User.username, (User.is_active, True)]


class SiteView(ModelView):
    fields = [
        Site.id,
        Site.user_id,
        Site.name,
        Site.description,
        Site.created_on,
        Site.updated_on,
    ]
    exclude_fields_from_list = [Site.description]
    exclude_fields_from_create = [Site.id, Site.created_on, Site.updated_on]
    exclude_fields_from_edit = [Site.id, Site.created_on, Site.updated_on]
    sortable_fields = [Site.name, Site.created_on, Site.updated_on]
    searchable_fields = [Site.id, Site.name]
    fields_default_sort = [Site.name, (Site.created_on, True)]


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


admin.add_view(UserView(User))
admin.add_view(SiteView(Site))
admin.add_view(DeviceView(Device))


admin.add_view(
    DropDown(
        "Resources",
        icon="fa fa-list",
        views=[
            ModelView(User),
            Link(label="Home Page", url="/admin"),
            # CustomView(label="Dashboard", path="/", template_path="dashboard.html"),
        ],
    )
)
