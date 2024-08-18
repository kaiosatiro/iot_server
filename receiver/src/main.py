import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.middleware import is_valid_uuid4
from fastapi import FastAPI, Request

from src.config import settings
from src.errors import unhandled_exception_handler
from src.logger.setup import setup_logging_config
from src.route.router import router

# from src.message_handler import MessageHandler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging_config()
    logger = logging.getLogger("lifespan")
    logger.info("StartUP")
    # message_handler = MessageHandler()
    yield  # {"message_handler": message_handler}
    logger.info("ShutDown")


app = FastAPI(
    title=settings.PROJECT_NAME,
    root_path=settings.RECEIVER_API_V1_STR,
    root_path_in_servers=True,
    lifespan=lifespan,
    exception_handlers={Exception: unhandled_exception_handler},
)

app.include_router(router)
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
    # generator=lambda: uuid.uuid4().hex,
    validator=is_valid_uuid4,
    # transformer=lambda a: a,
)


# Test route ---------------------------------------------------------------
@app.get("/test/", include_in_schema=False)
async def root(request: Request) -> dict[str, str]:
    logger = logging.getLogger("GET /test/")
    logger.info("Root")
    logger.info("Request ID: %s", request.headers["x-request-id"])
    return {"TEST": "PACMAN", "correlation_id": request.headers["x-request-id"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8100)
