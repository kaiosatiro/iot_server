from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI

from src.logger.setup import setup_logging
from src.core.config import settings
from src.api.main import api_router

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
    root_path_in_servers=True
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("StartUP")
    yield
    logger.info("ShutDown")


app.include_router(
    api_router,
)


@app.get("/")
async def root():
    logger.info("Root")
    return {"TEST": "PACMAN"}





# if __name__ == '__main__':
#     setup_logging()
#     logger = getLogger(__name__)
#     uvicorn.run(app, host="0.0.0.0", port=8000)
#     logger.info("Starting the User API service")

# Users:
# - GET /users - 200 OK | 403 Forbidden
# - GET /users/{id} - 200 OK | 403 Forbidden | 404 Not Found
# - POST /users - 201 Created | 400 Bad Request | 403 Forbidden | 409 Conflict
# - PUT /users/{id} - 200 OK | 400 Bad Request | 403 Forbidden | 404 Not Found
# - PATCH /users/{id} - 200 OK | 400 Bad Request | 403 Forbidden | 404 Not Found
# - DELETE /users/{id} - 204 No Content | 403 Forbidden | 404 Not Found

# Sites:
# - GET /sites - 200 OK | 403 Forbidden
# - GET /sites/{siteId} - 200 OK | 403 Forbidden | 404 Not Found
# - POST /sites - 201 Created | 400 Bad Request | 403 Forbidden
# - PUT /sites/{siteId} - 200 OK | 400 Bad Request | 403 Forbidden | 404 Not Found
# - DELETE /sites - 204 No Content | 403 Forbidden
# - DELETE /sites/{siteId} - 200 OK | 403 Forbidden | 404 Not Found

# Devices:
# - GET /devices - 200 OK | 404 Not Found | 403 Forbidden
# - GET /devices/{deviceId} - 200 OK | 404 Not Found | 403 Forbidden
# - GET /devices/site/{siteId} - 200 OK | 404 Not Found | 403 Forbidden
# - POST /devices - 201 Created | 400 Bad Request | 403 Forbidden
# - PUT /devices/{id} - 200 OK | 400 Bad Request | 403 Forbidden | 404 Not Found
# - DELETE /devices - 204 No Content | 404 Not Found
# - DELETE /devices/{deviceId} - 204 No Content | 404 Not Found
# - DELETE /devices/site/{siteId} - 204 No Content | 404 Not Found

# Messages:
# - GET /messages/{deviceId}?from=from&to=to&limit=limit - 200 OK | 404 Not Found
# - DELETE /messages/{messageId} - 204 No Content | 404 Not Found
# - DELETE /messages/device/{deviceId}?from=from&to=to&all=true - 204 OK | 404 Not Found
