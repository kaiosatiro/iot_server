import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from src import crud, utils
from src.api import dependencies as deps
from src.models import DefaultResponseMessage, Device, Message, MessagesListResponse

router = APIRouter()


@router.get("/device/{device_id}", response_model=MessagesListResponse)
async def get_messages_by_device_id(
    device_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
    from_: str | None = None,
    to: str | None = None,
    limit: int = 100,
    offset: int = 0
):
    from_ = from_ or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    to = to or (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    """
    Retrieve by Period and Device ID
    Defaut: Period of 24 hours
    Format:
        Complete: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
        Only date: '2024-07-22' %Y-%m-%d,
    Limit: 100 messages, Default: 100
    Offset: default: 0
    """
    logger = logging.getLogger("GET messages/device/{device_id}")

    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    #Validade datetime format
    if not utils.validate_datetime(from_) and not utils.validate_datetime(to):
        raise HTTPException(status_code=422, detail="Invalid datetime format")

    messages = crud.get_messages(
        db=session, device_id=device_id,
        start_date=from_, end_date=to,
        limit=limit, offset=offset
        )

    return MessagesListResponse(data=messages, count=len(messages))


@router.delete("/{message_id}", response_model=DefaultResponseMessage)
async def delete_message_by_id(
    message_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser
):
    """
    Delete by Message ID
    """
    logger = logging.getLogger("DELETE messages/{message_id}")

    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    device = session.get(Device, message.device_id)
    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    session.delete(message)
    session.commit()
    return DefaultResponseMessage(message="Message deleted")


@router.delete("/device/{device_id}", response_model=DefaultResponseMessage)
async def delete_messages_by_device_id(
    device_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
    from_: str | None = None,
    to: str | None = None,
    all: bool = False
):
    from_ = from_ or (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    to = to or (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    """
    Delete by Period and Device ID
    Defaut: Period of 24 hours
    Format:
        Complete: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
        Only date: '2024-07-22' %Y-%m-%d,
    All:False *** Delete ALL messages from the device ***
    """
    logger = logging.getLogger("DELETE messages/device/{device_id}")

    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if all:
        crud.delete_all_messages_per_device(db=session, device_id=device_id)
    else:
        if not utils.validate_datetime(from_) and not utils.validate_datetime(to):
            raise HTTPException(status_code=422, detail="Invalid datetime format")

        crud.delete_messages_by_period(
            db=session, device_id=device_id,
            start_date=from_, end_date=to
        )

    return DefaultResponseMessage(message="Messages deleted")
