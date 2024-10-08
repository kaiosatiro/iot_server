import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query

from src import crud, utils
from src.api import dependencies as deps
from src.models import (
    DefaultResponseMessage,
    Device,
    Message,
    MessageResponse,
    MessagesListResponse,
)

router = APIRouter()


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message_by_id(
    message_id: int, session: deps.SessionDep, current_user: deps.CurrentUser
) -> Message | HTTPException:
    """
    Retrieve by Message ID. The message must belong to a logged user's device.
    """
    logger = logging.getLogger("GET messages/{message_id}")
    logger.info("User %s is retrieving message %s", current_user.username, message_id)

    message = session.get(Message, message_id)
    if not message:
        logger.warning("Message %s not found", message_id)
        raise HTTPException(status_code=404, detail="Message not found")

    device = session.get(Device, message.device_id)
    if device and device.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, message_id %s",
            current_user.username,
            message_id,
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    logger.info("Returning message %s", message_id)
    return message


@router.get(
    "/device/{device_id}",
    response_model=MessagesListResponse,
    responses={
        404: deps.responses_404,
        401: deps.responses_401,
        403: deps.responses_403,
    },
)
async def get_messages_from_device(
    device_id: Annotated[int, Path(description="Device ID")],
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
    from_: str | None = Query(default=None, description="Initial datetime"),
    to: str | None = Query(default=None, description="Final datetime"),
    limit: int = Query(default=100, le=100),
    offset: int = 0,
) -> MessagesListResponse | HTTPException:
    from_ = from_ or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    to = to or (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    """
    Retrieve Messages by Device ID from logged user. It can be filtered by period.
    Defaut: Period of 24 hours
    Format:
        Complete: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
        Only date: '2024-07-22' %Y-%m-%d,
    Limit: 100 messages, Default: 100
    Offset: default: 0
    """
    logger = logging.getLogger("GET messages/device/{device_id}")
    logger.info(
        "User %s is retrieving messages from device %s",
        current_user.username,
        device_id,
    )

    device = session.get(Device, device_id)
    if not device:
        logger.warning("Device %s not found", device_id)
        raise HTTPException(status_code=404, detail="Device not found")

    if device.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, device_id %s",
            current_user.username,
            device_id,
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    # Validade datetime format
    if not utils.validate_datetime(from_) and not utils.validate_datetime(to):
        logger.warning("Invalid datetime format")
        raise HTTPException(status_code=422, detail="Invalid datetime format")

    messages = crud.get_messages(
        db=session,
        device_id=device_id,
        start_date=from_,
        end_date=to,
        limit=limit,
        offset=offset,
    )
    len_msg = len(messages)

    logger.info("Returning %s messages", len_msg)
    return MessagesListResponse(
        device_id=device_id, device_name=device.name, count=len_msg, data=messages
    )


@router.delete(
    "/{message_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DefaultResponseMessage,
)
async def delete_message_by_id(
    message_id: int, session: deps.SessionDep, current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete by Message ID
    """
    logger = logging.getLogger("DELETE messages/{message_id}")
    logger.info("User %s is deleting message %s", current_user.username, message_id)

    message = session.get(Message, message_id)
    if not message:
        logger.warning("Message %s not found", message_id)
        raise HTTPException(status_code=404, detail="Message not found")

    device = session.get(Device, message.device_id)
    if device and device.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, message_id %s",
            current_user.username,
            message_id,
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    session.delete(message)
    session.commit()

    logger.info("Message %s deleted successfully", message_id)
    return DefaultResponseMessage(message="Message deleted")


@router.delete(
    "/device/{device_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DefaultResponseMessage,
)
async def delete_messages_from_device(
    device_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
    from_: str | None = Query(default=None, description="Initial datetime"),
    to: str | None = Query(default=None, description="Final datetime"),
    all: Annotated[
        bool, Query(description="If True, delete all messages from the device")
    ] = False,
) -> DefaultResponseMessage | HTTPException:
    from_ = from_ or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    to = to or (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    """
    Retrieve Messages by Device ID from logged user. It can be done by period.
    Defaut: Period of 24 hours
    Format:
        Complete: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
        Only date: '2024-07-22' %Y-%m-%d,
    All:default=False *** Delete ALL messages from the device ***
    """
    logger = logging.getLogger("DELETE messages/device/{device_id}")
    logger.info(
        "User %s is deleting messages from device %s", current_user.username, device_id
    )

    device = session.get(Device, device_id)
    if not device:
        logger.warning("Device %s not found", device_id)
        raise HTTPException(status_code=404, detail="Device not found")

    if device.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, device_id %s",
            current_user.username,
            device_id,
        )
        raise HTTPException(status_code=403, detail="Forbidden")

    if all:
        crud.delete_all_messages_per_device(db=session, device_id=device_id)
    else:
        if not utils.validate_datetime(from_) and not utils.validate_datetime(to):
            logger.warning("Invalid datetime format")
            raise HTTPException(status_code=422, detail="Invalid datetime format")

        crud.delete_messages_by_period(
            db=session, device_id=device_id, start_date=from_, end_date=to
        )

    logger.info("Messages from device %s deleted successfully", device_id)
    return DefaultResponseMessage(message="Messages deleted")
