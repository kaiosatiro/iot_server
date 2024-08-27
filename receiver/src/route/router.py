import logging
from typing import Any

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    # Request,
    # BackgroundTasks,
)

import src.route.dependencies as deps
from src.config import settings
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
    payload: Any = Body(...),  # TODO: Try some type of JSON
) -> DefaultResponseMessage | HTTPException:
    """
    Endpoint that receives devices messages. Send messages to this endpoint with a **bearer** token. The messages body **must** be a JSON object.
    """
    logger = logging.getLogger(f"POST {settings.RECEIVER_API_V1_STR}")
    logger.info("Message Received in listener")
    # request.state.message_handler.process_message(device, payload)
    handler.process_message(device, payload)
    # background_tasks.add_task(handler.process_message, device, payload)
    # background_tasks.add_task(request.state.message_handler.process_message, device, payload)
    return DefaultResponseMessage(message="Accepted")


@router.post("/test-token", tags=["Listener"], response_model=DefaultResponseMessage)
def test_token(device: deps.CurrentDev) -> DefaultResponseMessage | HTTPException:
    """
    Test the **bearer** token before using it in the device.
    """
    logging.getLogger("/login/test-token").info(
        "Device %s is testing its own token", device
    )
    return DefaultResponseMessage(message=f"Token is valid. Device {device}")
