import logging

from fastapi import APIRouter, HTTPException
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


@router.get("/", response_model=DevicesListResponse)
async def get_devices(
    *,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> DevicesListResponse | HTTPException:
    """
    Retrieve Devices.
    """
    logger = logging.getLogger("GET devices/")

    count_statement = (
        select(func.count()).select_from(Device).where(Device.user_id == current_user.id))
    count = session.exec(count_statement).one()

    deviceslist = crud.get_devices_by_user_id(db=session, user_id=current_user.id)

    return DevicesListResponse(data=deviceslist, count=count)


@router.get("/site/{site_id}", response_model=DevicesListResponse)
async def get_devices_per_site(
    *,
    site_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser
) -> DevicesListResponse | HTTPException:
    """
    Create a new Device.
    """
    logger = logging.getLogger("POST devices/")

    if session.get(Site, site_id) is None:
        raise HTTPException(status_code=404, detail="Site not found")

    count_statement = (
        select(func.count())
        .select_from(Device)
        .where(Device.user_id == current_user.id)
        .where(Device.site_id == site_id)
        )
    count = session.exec(count_statement).one()

    device = crud.get_devices_by_site_id(db=session, site_id=site_id)

    return DevicesListResponse(data=device, count=count)


@router.post("/site", response_model=DeviceResponse, status_code=201)
async def create_a_device(
    *,
    session: deps.SessionDep,
    device_in: DeviceCreation,
    current_user: deps.CurrentUser
) -> DeviceResponse | HTTPException:
    """
    Create a new Device.
    """
    logger = logging.getLogger("POST devices/")

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


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_a_device(
    *,
    session: deps.SessionDep,
    device_id: int,
    device_in: DeviceUpdate,
    current_user: deps.CurrentUser
) -> DeviceResponse | HTTPException:
    """
    Update a Device.
    """
    logger = logging.getLogger("PATCH devices/")

    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        device = crud.update_device(db=session, db_device=device, device_new_input=device_in)
    except ValidationError as e:
        logger.info(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    return device


@router.delete("/{device_id}", response_model=DefaultResponseMessage)
async def delete_a_device(
    *,
    session: deps.SessionDep,
    device_id: int,
    current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete a Device.
    """
    logger = logging.getLogger("DELETE devices/")

    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_device(db=session, device=device)

    return DefaultResponseMessage(message="Device deleted")


@router.delete("/site/{site_id}", response_model=DefaultResponseMessage)
async def delete_devices_per_site(
    *,
    session: deps.SessionDep,
    site_id: int,
    current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete all Devices from a Site.
    """
    logger = logging.getLogger("DELETE devices/site/")

    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    if site.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_devices_per_site_id(db=session, site_id=site_id)

    return DefaultResponseMessage(message="Devices deleted")
