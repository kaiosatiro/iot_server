import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import src.doc as doc
from src.admin import admin
from src.api.main import api_router
from src.core.config import settings
from src.errors import unhandled_exception_handler
from src.logger.setup import setup_logging_config

setup_logging_config()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger = logging.getLogger("lifespan")
    logger.info("StartUP")
    yield
    logger.info("ShutDown")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_tags=doc.TAGS_METADATA,
    # summary=
    description=doc.DESCRIPTION,
    version=settings.VERSION,
    license_info=doc.LICENSE_INFO,
    # terms_of_service=
    contact=doc.CONTACT,
    swagger_ui_parameters={"operationsSorter": "method"},
    # swagger_static={
    #     "favicon": "icon.ico",
    # },
    root_path=settings.USERAPI_API_V1_STR,
    root_path_in_servers=True,
    lifespan=lifespan,
    exception_handlers={Exception: unhandled_exception_handler},
)

app.include_router(api_router)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
    # generator=lambda: uuid.uuid4().hex,
    validator=is_valid_uuid4,
    # transformer=lambda a: a,
)
# app.mount("/admin", admin)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
admin.mount_to(app)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse("src/static/icon.ico")


# Test route ---------------------------------------------------------------
@app.get("/test", include_in_schema=False)
async def root(request: Request) -> dict[str, str]:
    logger = logging.getLogger("Test Route")
    logger.info("Root")
    logger.info("Request ID: %s", request.headers["x-request-id"])
    return {
        "TEST": "USERAPI",
        "root_path": request.scope.get("root_path") or "",
        "request_id": request.headers["x-request-id"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# Login:
# - POST /access-token - 200 | 401
# - POST /login/test-token - 200 | 401
# - POST /password-recovery/{email} - 200 | 404 | 400
# - POST /reset-password - 200 | 400 | 401 | 404

# Users:
# - POST users/signup - 201 | 403 | 409 | 422
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
