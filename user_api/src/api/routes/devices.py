import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import ValidationError
from sqlmodel import func, select

from src import crud
from src.api import dependencies as deps
from src.api.rpc import rpcCall
from src.models import (
    DefaultResponseMessage,
    Device,
    DeviceCreation,
    DeviceResponse,
    DevicesListResponse,
    DeviceUpdate,
    Environment,
)

router = APIRouter()


@router.get(
    "/", responses={401: deps.responses_401}, response_model=DevicesListResponse
)
async def get_user_devices(
    *, session: deps.SessionDep, current_user: deps.CurrentUser
) -> DevicesListResponse | HTTPException:
    """
    Retrieve all Devices from logged User.
    """
    logger = logging.getLogger("GET devices/")
    logger.info("getting all devices from user %s", current_user.username)

    count_statement = (
        select(func.count())
        .select_from(Device)
        .where(Device.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    deviceslist = crud.get_devices_by_owner_id(db=session, owner_id=current_user.id)

    # if logger.isEnabledFor(logging.DEBUG): logger.debug(f"Count: {count}")
    logger.info("Returning %s devices", count)
    return DevicesListResponse(
        owner_id=current_user.id,
        username=current_user.username,
        count=count,
        data=deviceslist,
    )


@router.get(
    "/{device_id}",
    responses={
        401: deps.responses_401,
        404: deps.responses_404,
        403: deps.responses_403,
    },
    response_model=DeviceResponse,
)
async def get_device_information(
    *,
    device_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> Device | HTTPException:
    """
    Retrieve a Device information by ID.
    """
    logger = logging.getLogger("GET devices/")
    logger.info("getting device %s from user %s", device_id, current_user.username)

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
        raise HTTPException(status_code=403, detail="Not enough permissions")

    logger.info("Returning device %s", device_id)
    return device


@router.get(
    "/environment/{environment_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DevicesListResponse,
)
async def get_environment_devices(
    *, environment_id: int, session: deps.SessionDep, current_user: deps.CurrentUser
) -> DevicesListResponse | HTTPException:
    """
    Get all devices from the specific Environment.
    The environment must belong to the logged User.
    """
    logger = logging.getLogger("POST devices/")
    logger.info(
        "getting all devices from environment %s from user %s",
        environment_id,
        current_user.username,
    )

    environment = session.get(Environment, environment_id)
    if not environment:
        logger.warning("Environment %s not found", environment_id)
        raise HTTPException(status_code=404, detail="Environment not found")

    count_statement = (
        select(func.count())
        .select_from(Device)
        .where(Device.owner_id == current_user.id)
        .where(Device.environment_id == environment_id)
    )
    count = session.exec(count_statement).one()

    device = crud.get_devices_by_environment_id(
        db=session, environment_id=environment_id
    )

    logger.info("Returning %s devices from environment %s", count, environment_id)
    return DevicesListResponse(
        owner_id=current_user.id,
        username=current_user.username,
        environment_id=environment_id,
        environment_name=environment.name,
        count=count,
        data=device,
    )


@router.post(
    "/environment",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DeviceResponse,
    status_code=201,
)
async def create_device(
    *,
    session: deps.SessionDep,
    device_in: DeviceCreation,
    current_user: deps.CurrentUser,
    background_tasks: BackgroundTasks,
    rpcCall: rpcCall,
) -> Device | HTTPException:
    """
    Create a new Device, **"name"** and **"environment_id"** are required.
    """
    logger = logging.getLogger("POST devices/")
    logger.info("Creating device %s from user %s", device_in.name, current_user.id)

    environment = session.get(Environment, device_in.environment_id)

    if environment is None:
        logger.warning("Environment %s not found", device_in.environment_id)
        raise HTTPException(status_code=404, detail="Environment not found")

    if environment.owner_id != current_user.id:
        logger.warning(
            "Environment %s does not belong to user %s",
            environment.id,
            current_user.username,
        )
        raise HTTPException(
            status_code=403, detail="Environment does not belong to user"
        )

    try:
        device_in.owner_id = current_user.id
        device = crud.create_device(db=session, device_input=device_in)
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    background_tasks.add_task(
        rpcCall.add_device_handler_cache, device.id
    )  # add to Handler service cache

    logger.info("Device %s created", device.id)
    return device


@router.patch(
    "/{device_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DeviceResponse,
)
async def update_device(
    *,
    session: deps.SessionDep,
    device_id: int,
    device_in: DeviceUpdate,
    current_user: deps.CurrentUser,
) -> Device | HTTPException:
    """
    Update the Device information. If the **"environment_id"** is changed,
    the new Environment must belong to the logged User.
    """
    logger = logging.getLogger("PATCH devices/")
    logger.info("Updating device %s from user %s", device_id, current_user.username)

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
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if device_in.environment_id:
        environment = session.get(Environment, device_in.environment_id)
        if environment is None or environment.owner_id != current_user.id:
            logger.warning(
                "Environment %s not found or does not belong to user",
                device_in.environment_id,
            )
            raise HTTPException(status_code=404, detail="Environment not found")

    try:
        device = crud.update_device(
            db=session, db_device=device, device_new_input=device_in
        )
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    logger.info("Device %s updated", device_id)
    return device


@router.delete(
    "/{device_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DefaultResponseMessage,
)
async def delete_device(
    *,
    session: deps.SessionDep,
    device_id: int,
    current_user: deps.CurrentUser,
    background_tasks: BackgroundTasks,
    rpcCall: rpcCall,
) -> DefaultResponseMessage | HTTPException:
    """
    Delete a Device by its ID and **consequently** all its messages.

    """
    logger = logging.getLogger("DELETE devices/")
    logger.info("Deleting device %s from user %s", device_id, current_user.username)

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
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_device(db=session, device=device)

    background_tasks.add_task(
        rpcCall.remove_device_handler_cache, device_id
    )  # remove from Handler service cache

    logger.info("Device %s deleted", device_id)
    return DefaultResponseMessage(message="Device deleted")


@router.delete(
    "/environment/{environment_id}",
    responses={
        404: deps.responses_404,
        403: deps.responses_403,
        401: deps.responses_401,
    },
    response_model=DefaultResponseMessage,
)
async def delete_environment_devices(
    *, session: deps.SessionDep, environment_id: int, current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete all Devices from a Environment, **consequently** all its messages.
    The environment must belong to the logged User.
    """
    logger = logging.getLogger("DELETE devices/environment/")
    logger.info(
        "Deleting all devices from environment %s from user %s",
        environment_id,
        current_user.username,
    )

    environment = session.get(Environment, environment_id)
    if not environment:
        logger.warning("Environment %s not found", environment_id)
        raise HTTPException(status_code=404, detail="Environment not found")

    if environment.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, environment_id %s",
            current_user.username,
            environment_id,
        )
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_devices_per_environment_id(db=session, environment_id=environment_id)

    logger.info("Devices from environment %s deleted", environment_id)
    return DefaultResponseMessage(message="Devices deleted")
