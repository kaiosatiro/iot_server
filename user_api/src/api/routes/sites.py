import logging

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from sqlmodel import func, select

import src.api.dependencies as deps
from src import crud
from src.models import (
    DefaultResponseMessage,
    Site,
    SiteCreation,
    SiteResponse,
    SitesListResponse,
    SiteUpdate,
)

router = APIRouter()


@router.post(
    "/",
    responses={401: deps.responses_401, 403: deps.responses_403},
    response_model=SiteResponse,
    status_code=201,
)
async def create_site(
    *, session: deps.SessionDep, site_in: SiteCreation, current_user: deps.CurrentUser
) -> Site | HTTPException:
    """
    Create a new Site with a logged User. The **"name"** is required.
    """
    logger = logging.getLogger("POST sites/")
    logger.info("User %s is creating a new site", current_user.username)

    try:
        site = crud.create_site(db=session, site_input=site_in, owner_id=current_user.id)
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    logger.info("Site %s created successfully", site.name)
    return site


@router.get(
    "/user",
    responses={401: deps.responses_401, 403: deps.responses_403},
    response_model=SitesListResponse,
)
async def get_all_sites_from_user(
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> SitesListResponse | HTTPException:
    """
    Retrieve all Sites from a logged User.
    """
    logger = logging.getLogger("GET sites/user")
    logger.info("User %s is retrieving all sites", current_user.username)

    count_statement = (
        select(func.count()).select_from(Site).where(Site.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    Siteslist = crud.get_sites_by_owner_id(db=session, owner_id=current_user.id)

    logger.info("Returning %s sites", count)
    return SitesListResponse(
        owner_id=current_user.id,
        username=current_user.username,
        count=count,
        data=Siteslist,
    )


@router.get(
    "/{site_id}",
    responses={
        401: deps.responses_401,
        403: deps.responses_403,
        404: deps.responses_404,
    },
    response_model=SiteResponse,
)
async def get_information_from_site(
    site_id: int,
    session: deps.SessionDep,
    current_user: deps.CurrentUser,
) -> Site | HTTPException:
    """
    Retrieve a Site by ID from a logged User.
    """
    logger = logging.getLogger("GET sites/user")
    logger.info("User %s is retrieving site %s", current_user.username, site_id)

    site = session.get(Site, site_id)
    if not site:
        logger.warning("Site %s not found", site_id)
        raise HTTPException(status_code=404, detail="Site not found")
    elif site.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, site_id %s",
            current_user.username,
            site_id,
        )
        raise HTTPException(status_code=403, detail="Not enough permissions")

    logger.info("Returning site %s", site_id)
    return site


@router.patch(
    "/{site_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=SiteResponse,
)
async def update_site(
    *,
    session: deps.SessionDep,
    site_id: int,
    site_in: SiteUpdate,
    current_user: deps.CurrentUser,
) -> Site | HTTPException:
    """
    Update a Site information by its ID from a logged User.
    """
    logger = logging.getLogger("PATCH sites/")
    logger.info("User %s is updating site %s", current_user.username, site_id)

    site = session.get(Site, site_id)

    if not site:
        logger.warning("Site %s not found", site_id)
        raise HTTPException(status_code=404, detail="Site not found")

    if site.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, site_id %s",
            current_user.username,
            site_id,
        )
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        site = crud.update_site(db=session, db_site=site, site_new_input=site_in)
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=422, detail="Bad body format")

    logger.info("Site %s updated", site_id)
    return site


@router.delete(
    "/{site_id}",
    responses={404: deps.responses_404, 403: deps.responses_403},
    response_model=DefaultResponseMessage,
)
async def delete_site(
    *, session: deps.SessionDep, site_id: int, current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete Site, **it will** delete its devices and **consequently** its messages.
    """
    logger = logging.getLogger("DELETE sites/")
    logger.info("User %s is deleting site %s", current_user.username, site_id)

    site = session.get(Site, site_id)

    if not site:
        logger.warning("Site %s not found", site_id)
        raise HTTPException(status_code=404, detail="Site not found")

    if site.owner_id != current_user.id:
        logger.warning(
            "User %s does not have permissions, site_id %s",
            current_user.username,
            site_id,
        )
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_site(db=session, site=site)

    logger.info("Site %s deleted", site_id)
    return DefaultResponseMessage(message="Site deleted successfully")
