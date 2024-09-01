from src.admin.device_view import DeviceView
from src.admin.main import admin
from src.admin.messages_view import MessageView
from src.admin.site_view import SiteView
from src.admin.user_view import UserView
from src.models import Device, Message, Site, User

# admin.add_view(Link(label="Home Page", icon="fa fa-link", url="/"))
admin.add_view(UserView(User, identity="users"))
admin.add_view(SiteView(Site, identity="sites"))
admin.add_view(DeviceView(Device, identity="devices"))
admin.add_view(MessageView(Message, identity="messages"))


# admin.add_view(
#     DropDown(
#         "Resources",
#         icon="fa fa-list",
#         views=[
#             ModelView(User),
#             Link(label="Home Page", url="/admin"),
#             # CustomView(label="Dashboard", path="/", template_path="dashboard.html"),
#         ],
#     )
# )
