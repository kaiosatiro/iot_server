from src.admin.device_view import DeviceView
from src.admin.environment_view import EnvironmentView
from src.admin.home_view import HomeView
from src.admin.main import admin
from src.admin.messages_view import MessageView
from src.admin.user_view import UserView
from src.models import Device, Environment, Message, User

# admin.add_view(Link(label="Home Page", icon="fa fa-link", url="/"))
admin.add_view(HomeView(label="Home", icon="fa fa-home", path="/"))
admin.add_view(UserView(User, identity="users", icon="fa fa-user"))
admin.add_view(
    EnvironmentView(Environment, identity="environments", icon="fa fa-building")
)
admin.add_view(DeviceView(Device, identity="devices", icon="fa fa-server"))
admin.add_view(MessageView(Message, identity="messages", icon="fa fa-envelope"))


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
