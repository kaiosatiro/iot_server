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
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Sites",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Devices",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Messages",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Admin",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(
    # debug=True,
    title=settings.PROJECT_NAME,
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"operationsSorter": "method"},
    # summary=
    # description=
    version=settings.VERSION,
    # openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # terms_of_service=
    # contact=
    # license_info=
    root_path=settings.API_V1_STR,
    root_path_in_servers=True,
)

app.include_router(
    api_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("StartUP")
    yield
    logger.info("ShutDown")


@app.get("/")
async def root():
    logger.info("Root")
    return {"TEST": "PACMAN"}


# if __name__ == '__main__':
#     setup_logging()
#     logger = getLogger(__name__)
#     uvicorn.run(app, host="0.0.0.0", port=8000)
#     logger.info("Starting the User API service")

# Login:
# - POST /access-token - 200 | 401 Unauthorized

# Users:
# - GET /users/me - 200 | 404
# - PATCH /users/me/ - 200 | 422 | 404 | 409
# - PATCH /users/me/password - 200 | 422 | 404 |
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
# - GET /sites - 200 | 401
# - POST /sites - 201 | 400 | 403
# - PATCH /sites/{site_id} - 200 | 400 | 403 | 404
# - DELETE /sites/{site_id} - 200 | 403 | 404

# Devices:
# - GET /devices - 200 | 404 | 403
# - GET /devices/site/{site_id} - 200 | 403 | 404
# - POST /devices/site - 201 | 400 | 403
# - PATCH /devices/{device_id} - 200 | 422  | 403  | 404
# - DELETE /devices/{device_id} - 200 | 404
# - DELETE /devices/site/{site_id} - 200 | 404

# Messages:
# - GET /messages/device/{device_id}?from=from&to=to&limit=limit&offset=offset - 200 | 404 | 401 | 403
# - DELETE /messages/{message_id} - 200 | 404 | 403
# - DELETE /messages/device/{device_id}?from=from&to=to&all=true - 200 | 404
