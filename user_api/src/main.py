from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from src.api.main import api_router
from src.core.config import settings
from src.logger.setup import setup_logging

setup_logging()
logger = getLogger(__name__)

tags_metadata = [
    {
        "name": "Login",
        "description": "To authenticate and get an access token.",
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

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_tags=tags_metadata,
    # summary=
    description=description,
    version=settings.VERSION,
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
    # terms_of_service=
    contact={
        "name": "Caio Satiro",
        "url": "https://github.com/kaiosatiro",
        "email": "gaiusSatyr@gmail.com",
    },
    swagger_ui_parameters={"operationsSorter": "method"},
    root_path=settings.API_V1_STR,
    root_path_in_servers=True,
)

app.include_router(api_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("StartUP")
    yield
    logger.info("ShutDown")


@app.get("/", include_in_schema=False)
async def root():
    logger.info("Root")
    return {"TEST": "PACMAN"}


# Login:
# - POST /access-token - 200 | 401 Unauthorized

# Users:
# - GET /users/me - 200 | 404
# - PATCH /users/me/ - 200 | 422 | 404 | 409
# - PATCH /users/me/password - 200 | 409 | 404 | 422
# - DELETE /users/me - 200 | 403 | 404

# Admin:
# - GET /users - 200 | 401 | 403 | 404
# - GET /users/{id} - 200 | 403 | 404
# - POST /users - 201 | 422 | 403 | 409
# - PATCH /users/{id} - 200 | 422 | 403 | 404 | 409
# - DELETE /users/{id} - 200 | 403 | 404

# - GET /sites - 200 | 401
# - GET /devices - 200 | 404 | 403

# Sites:
# - GET /sites/user - 200 | 401
# - GET /sites/{site_id} - 200 | 403 | 404
# - POST /sites - 201 | 400 | 403
# - PATCH /sites/{site_id} - 200 | 400 | 403 | 404
# - DELETE /sites/{site_id} - 200 | 403 | 404

# Devices:
# - GET /devices - 200 | 404 | 403
# - GET /devices/{device_id} - 200 | 404 | 403
# - GET /devices/site/{site_id} - 200 | 403 | 404
# - POST /devices/site - 201 | 400 | 403
# - PATCH /devices/{device_id} - 200 | 422  | 403  | 404
# - DELETE /devices/{device_id} - 200 | 404
# - DELETE /devices/site/{site_id} - 200 |
# - POST /sites - 201 | 400 | 403
# - PATCH /sites/{site_id} - 200 | 400 | 403 | 404
# - DELETE /sites/{site_id} - 200 | 403 | 404

# Messages:
# - GET /messages/{message_id} - 200 | 404 | 403
# - GET /messages/device/{device_id}?from=from&to=to&limit=limit&offset=offset - 200 | 404 | 401 | 403
# - DELETE /messages/{message_id} - 200 | 404 | 403
# - DELETE /messages/device/{device_id}?from=from&to=to&all=true - 200 | 404
