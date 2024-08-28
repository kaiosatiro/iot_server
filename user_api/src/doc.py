from src.core.config import settings

TAGS_METADATA = [
    {
        "name": "Login",
        "description": "Authenticate and get an access token.",
    },
    {
        "name": "Users",
        "description": "Operations with Users. **Needs** to be authenticated.",
    },
    {
        "name": "Sites",
        "description": "Operations with Sites. **Needs** to be authenticated.",
    },
    {
        "name": "Devices",
        "description": "Operations with Devices. **Needs** to be authenticated.",
    },
    {
        "name": "Messages",
        "description": "Retrive and delete Messages from devices. **Needs** to be authenticated.",
    },
    {
        "name": "Admin",
        "description": "Manage Users. Super User **Needs** to be authenticated.",
    },
]

DESCRIPTION = f"""
## IoT Server Aplication.

API documentation for the **User API**, which is responsible for managing users, sites, and devices.\n
**Swagger UI version at:** [{settings.USERAPI_API_V1_STR}/docs]({settings.USERAPI_API_V1_STR}/docs)\n
**Redoc version at:** [{settings.USERAPI_API_V1_STR}/redoc]({settings.USERAPI_API_V1_STR}/redoc)\n

#### Messages listener:
The device messages are received in the **Device API** endpoint: **[{settings.RECEIVER_API_V1_STR}/]({settings.RECEIVER_API_V1_STR})**\n
**Devices API docs:** [{settings.RECEIVER_API_V1_STR}/docs]({settings.RECEIVER_API_V1_STR}/docs)\n

#### **See the repository at [GitHub](https://github.com/kaiosatiro/iot_server)**
"""

LICENSE_INFO = {
    "name": "Apache 2.0",
    "identifier": "MIT",
}

# TERMS_OF_SERVICE = {

# }

CONTACT = {
    "name": "Gaius Satyr",
    "url": "https://github.com/kaiosatiro",
    "email": "gaiusSatyr@mail.com",
}
