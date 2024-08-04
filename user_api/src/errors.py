import logging

from asgi_correlation_id import correlation_id
from fastapi import HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger = logging.getLogger(f"{request.method} {request.url.path} EXCEPTION")
    logger.critical("Unhandled exception: %s", exc)
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            "Internal server error",
            headers={"X-Request-ID": correlation_id.get() or ""},
        ),
    )
