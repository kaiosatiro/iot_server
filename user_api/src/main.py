from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from src.api.main import api_router
from src.core.config import settings
from src.logger.setup import setup_logging

setup_logging()
logger = getLogger(__name__)

app = FastAPI(
    # debug=True,
    title=settings.PROJECT_NAME,
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
# - GET /users - 200 | 401 | 403 | 404
# - GET /users/me - 200 | 404
# - GET /users/{id} - 200 | 403 | 404
# - POST /users - 201 | 422 | 403 | 409
# - PATCH /users/{id} - 200 | 422 | 403 | 404 | 409
# - PATCH /users/me/ - 200 | 422 | 404 | 409
# - PATCH /users/me/password - 200 | 422 | 404 | 401
# - DELETE /users/{id} - 200 | 403 | 404

# Sites | Devices | Messages:

# - GET /sites - 200 | 403
# - POST /sites - 201 | 400 | 403
# - PATCH /sites/{siteId} - 200 | 400 | 403 | 404
# - DELETE /sites/{siteId} - 200 | 403 | 404

# - GET /devices - 200 | 404 | 403
# - GET /devices/site/{siteId} - 200 | 403 | 404
# - POST /devices - 201 Created | 400 | 403
# - PATCH /devices/{id} - 200 | 400  | 403  | 404
# - DELETE /devices/{deviceId} - 200 | 404
# - DELETE /devices/site/{siteId} - 200 | 404

# - GET /messages/device/{deviceId}?from=from&to=to&limit=limit - 200 | 404 | 403
# - DELETE /messages/{messageId} - 200 | 404 
# - DELETE /messages/device/{deviceId}?from=from&to=to&all=true - 200 | 404
