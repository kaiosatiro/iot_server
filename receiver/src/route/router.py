import logging

from fastapi import APIRouter, HTTPException

from src.models import DefaultResponseMessage
from src.message_handler import MessageHandler
import src.route.dependencies as deps

router = APIRouter()

@router.get(
        "/",
        tags=["listener"],
        response_model=DefaultResponseMessage,
        responses={403: deps.responses_403, 422: deps.responses_422},
        status_code=202,
    )
async def listener(device: deps.CurrentDev) -> DefaultResponseMessage | HTTPException:
    """
    Listener endpoint. The devices will send messages to this endpoint with a token.
    """
    logger = logging.getLogger("listener")
    logger.info("Message Received endpoint")

    return DefaultResponseMessage(message="ok")
    