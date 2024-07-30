import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError
from sqlmodel import func, select

from src import crud
from src.api import dependencies as deps
from src.models import (
    DefaultResponseMessage,
    Device,
    DeviceCreation,
    DeviceResponse,
    DevicesListResponse,
    DeviceUpdate,
    Site,
)


router = APIRouter()


@router.get(
        "/",
        responses={401: deps.responses_401},
        response_model=DevicesListResponse)
async def get_user_devices(
    *,
    session: deps.SessionDep,
    current_user: deps.CurrentUser
) -> DevicesListResponse | HTTPException:
    """
    Retrieve all Devices from logged User.
    """
    logger = logging.getLogger("GET devices/")
    logger.info("getting all devices from user %s", current_user.username)

    count_statement = (
        select(func.count()).select_from(Device).where(Device.user_id == current_user.id))
    count = session.exec(count_statement).one()

    deviceslist = crud.get_devices_by_user_id(db=session, user_id=current_user.id)

    # if logger.isEnabledFor(logging.DEBUG): logger.debug(f"Count: {count}")
    return DevicesListResponse(
        user_id=current_user.id,
        username=current_user.username,
        count=count,
        data=deviceslist
    )


@router.get(
        "/{device_id}",
        responses={401: deps.responses_401, 404: deps.responses_404, 403: deps.responses_403}, 
        response_model=DeviceResponse)
async def get_device_information(
    *,
    device_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> DeviceResponse | HTTPException:
    """
    Retrieve a Device information by ID.
    """
    logger = logging.getLogger("GET devices/")
    logger.info("getting device %s from user %s", device_id, current_user.username)

    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return device


@router.get(
        "/site/{site_id}",
        responses={404: deps.responses_404, 403: deps.responses_403}, 
        response_model=DevicesListResponse)
async def get_site_devices(
    *,
    site_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser
) -> DevicesListResponse | HTTPException:
    """
    Get all devices from the specific Site.
    The site must belong to the logged User.
    """
    logger = logging.getLogger("POST devices/")
    logger.info("getting all devices from site %s from user %s", site_id, current_user.username)

    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    count_statement = (
        select(func.count())
        .select_from(Device)
        .where(Device.user_id == current_user.id)
        .where(Device.site_id == site_id)
        )
    count = session.exec(count_statement).one()

    device = crud.get_devices_by_site_id(db=session, site_id=site_id)

    return DevicesListResponse(
        user_id=current_user.id,
        username=current_user.username,
        site_id=site_id,
        site_name=site.name,
        count=count,
        data=device
    )


@router.post(
        "/site",
        responses={404: deps.responses_404, 403: deps.responses_403},
        response_model=DeviceResponse, status_code=201)
async def create_device(
    *,
    session: deps.SessionDep,
    device_in: DeviceCreation,
    current_user: deps.CurrentUser
) -> DeviceResponse | HTTPException:
    """
    Create a new Device, **"name"** and **"site_id"** are required.
    """
    logger = logging.getLogger("POST devices/")
    logger.info("Creating device %s from user %s", device_in.name, current_user)

    site = session.get(Site, device_in.site_id)

    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")

    if site.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Site does not belong to user")

    try:
        device_in.user_id = current_user.id
        device = crud.create_device(db=session, device_input=device_in)
    except ValidationError as e:
        logger.info(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    return device


@router.patch(
        "/{device_id}",
        responses={404: deps.responses_404, 403: deps.responses_403},
        response_model=DeviceResponse)
async def update_device(
    *,
    session: deps.SessionDep,
    device_id: int,
    device_in: DeviceUpdate,
    current_user: deps.CurrentUser
) -> DeviceResponse | HTTPException:
    """
    Update the Device information. If the **"site_id"** is changed,
    the new Site must belong to the logged User.
    """
    logger = logging.getLogger("PATCH devices/")
    logger.info("Updating device %s from user %s", device_id, current_user.username)

    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if device_in.site_id:
        site = session.get(Site, device_in.site_id)
        if site is None or site.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Site not found")

    try:
        device = crud.update_device(db=session, db_device=device, device_new_input=device_in)
    except ValidationError as e:
        logger.info(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    return device


@router.delete(
        "/{device_id}",
        responses={404: deps.responses_404, 403: deps.responses_403},
        response_model=DefaultResponseMessage)
async def delete_device(
    *,
    session: deps.SessionDep,
    device_id: int,
    current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete a Device by its ID and **consequently** all its messages.
    
    """
    logger = logging.getLogger("DELETE devices/")
    logger.info("Deleting device %s from user %s", device_id, current_user.username)

    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_device(db=session, device=device)

    return DefaultResponseMessage(message="Device deleted")


@router.delete(
        "/site/{site_id}",
        responses={404: deps.responses_404, 403: deps.responses_403, 401: deps.responses_401},
        response_model=DefaultResponseMessage)
async def delete_site_devices(
    *,
    session: deps.SessionDep,
    site_id: int,
    current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete all Devices from a Site, **consequently** all its messages. 
    The site must belong to the logged User. 
    """
    logger = logging.getLogger("DELETE devices/site/")
    logger.info("Deleting all devices from site %s from user %s", site_id, current_user.username)

    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    if site.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_devices_per_site_id(db=session, site_id=site_id)

    return DefaultResponseMessage(message="Devices deleted")
