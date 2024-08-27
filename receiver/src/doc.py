from src.config import settings

TAGS_METADATA = [
    {
        "name": "Listener",
        "description": "Devices listener endpoint.",
    },
]

DESCRIPTION = f"""
## IoT Server Aplication.

API documentation for the **Device Messages API**.\n

The device messages are received on this server

**Users API docs at:** [{settings.USERAPI_API_V1_STR}/docs]({settings.USERAPI_API_V1_STR}/docs)\n

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
