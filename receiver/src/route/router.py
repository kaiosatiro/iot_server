import logging
from typing import Any

from fastapi import APIRouter, Body, HTTPException

import src.route.dependencies as deps
from src.message_handler import message_handler
from src.models import DefaultResponseMessage

router = APIRouter()


@router.post(
    "/",
    tags=["Listener"],
    response_model=DefaultResponseMessage,
    responses={403: deps.responses_403, 422: deps.responses_422},
    status_code=202,
)
async def listener(
    device: deps.CurrentDev,
    # request: Request,
    handler: message_handler,
    # background_tasks: BackgroundTasks,
    payload: Any = Body(...),
) -> DefaultResponseMessage | HTTPException:
    """
    Endpoint that receives devices messages. Send messages to this endpoint with a token.
    """
    logger = logging.getLogger("POST listener/v1/")
    logger.info("Message Received in listener")
    # request.state.message_handler.process_message(device, payload)
    handler.process_message(device, payload)
    # background_tasks.add_task(handler.process_message, device, payload)
    # background_tasks.add_task(request.state.message_handler.process_message, device, payload)
    return DefaultResponseMessage(message="Accepted")
