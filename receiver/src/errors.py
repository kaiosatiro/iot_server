import logging

from asgi_correlation_id import correlation_id
from fastapi import HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import Response


async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
    logger = logging.getLogger(f"{request.method} {request.url.path} EXCEPTION")
    logger.critical("Unhandled exception: %s", exc)
    req_id = correlation_id.get() or ""
    return await http_exception_handler(
        request,
        HTTPException(
            500,
            f"Internal server error, please contact the administrator. Resquest ID: {req_id}",
            headers={"X-Request-ID": req_id},
        ),
    )
