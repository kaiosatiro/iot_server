import logging

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from sqlmodel import func, select

import src.api.dependencies as deps
from src import crud
from src.models import (
    DefaultResponseMessage,
    Environment,
    EnvironmentCreation,
    EnvironmentListResponse,
    EnvironmentResponse,
    EnvironmentUpdate,
)

router = APIRouter()


@router.post(
    "/",
    responses={401: deps.responses_401, 403: deps.responses_403},
    response_model=EnvironmentResponse,
    status_code=201,
)
async def create_environment(
    *,
    session: deps.SessionDep,
    environment_in: EnvironmentCreation,
    current_user: deps.CurrentUser,
) -> Environment | HTTPException:
    """
    Create a new Environment with a logged User. The **"name"** is required.
    """
    logger = logging.getLogger("POST environments/")
    logger.info("User %s is creating a new environment", current_user.username)

    try:
        environment = crud.create_environment(
            db=session, environment_input=environment_in, owner_id=current_user.id
        )
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    logger.info("Environment %s created successfully", environment.name)
    return environment


@router.get(
    "/user",
    responses={401: deps.responses_401, 403: deps.responses_403},
    response_model=EnvironmentListResponse,
)
async def get_all_environments_from_user(
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> EnvironmentListResponse | HTTPException:
    """
    Retrieve all Environments from a logged User.
    """
    logger = logging.getLogger("GET environments/user")
    logger.info("User %s is retrieving all environments", current_user.username)

    count_statement = (
        select(func.count())
        .select_from(Environment)
        .where(Environment.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    Environmentlist = crud.get_environments_by_owner_id(
        db=session, owner_id=current_user.id
    )

    logger.info("Returning %s environments", count)
    return EnvironmentListResponse(
        owner_id=current_user.id,
        username=current_user.username,
        count=count,
        data=Environmentlist,
    )


@router.get(
    "/{environment_id}",
    responses={
        401: deps.responses_401,
        403: deps.responses_403,
        404: deps.responses_404,
    },
    response_model=EnvironmentResponse,
)
async def get_information_from_environment(
    environment_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> Environment | HTTPException:
    """
    Retrieve a Environment by ID from a logged User.
    """
    logger = logging.getLogger("GET environments/user")
    logger.info(
        "User %s is retrieving environment %s", current_user.username, environment_id
    )

    environment = session.get(Environment, environment_id)
    if not environment:
        logger.warning("Environment %s not found", environment_id)
        raise HTTPException(status_code=404, detail="Environment not found")
    elif environment.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, environment_id %s",
            current_user.username,
            environment_id,
        )
        raise HTTPException(status_code=403, detail="Not enough permissions")

    logger.info("Returning environment %s", environment_id)
    return environment


@router.patch(
    "/{environment_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=EnvironmentResponse,
)
async def update_environment(
    *,
    session: deps.SessionDep,
    environment_id: int,
    environment_in: EnvironmentUpdate,
    current_user: deps.CurrentUser,
) -> Environment | HTTPException:
    """
    Update a Environment information by its ID from a logged User.
    """
    logger = logging.getLogger("PATCH environments/")
    logger.info(
        "User %s is updating environment %s", current_user.username, environment_id
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

    try:
        environment = crud.update_environment(
            db=session, db_environment=environment, environment_new_input=environment_in
        )
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    logger.info("Environment %s updated", environment_id)
    return environment


@router.delete(
    "/{environment_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DefaultResponseMessage,
)
async def delete_environment(
    *, session: deps.SessionDep, environment_id: int, current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete Environment, **it will** delete its devices and **consequently** its messages.
    """
    logger = logging.getLogger("DELETE environments/")
    logger.info(
        "User %s is deleting environment %s", current_user.username, environment_id
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

    crud.delete_environment(db=session, environment=environment)

    logger.info("Environment %s deleted", environment_id)
    return DefaultResponseMessage(message="Environment deleted successfully")
