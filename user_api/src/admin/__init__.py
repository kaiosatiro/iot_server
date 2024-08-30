from src.admin.main import admin
from src.admin.user_view import UserView
from src.admin.site_view import SiteView
from src.admin.device_view import DeviceView
from src.models import User, Device, Site


admin.add_view(UserView(User))
admin.add_view(SiteView(Site))
admin.add_view(DeviceView(Device))


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

