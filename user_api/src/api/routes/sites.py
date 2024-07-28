import logging
from typing import Any

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


@router.get("/", response_model=SitesListResponse)
async def get_sites(
    session: deps.SessionDep,
    current_user: deps.CurrentUser
) -> Any:
    """
    Retrieve Sites.
"""
    logger = logging.getLogger("GET sites/")

    count_statement = (
        select(func.count()).select_from(Site).where(Site.user_id == current_user.id))
    count = session.exec(count_statement).one()

    Siteslist = crud.get_sites_by_user_id(db=session, user_id=current_user.id)

    return SitesListResponse(data=Siteslist, count=count)


@router.post("/", response_model=SiteResponse, status_code=201)
async def create_a_site(
    *,
    session: deps.SessionDep,
    site_in: SiteCreation,
    current_user: deps.CurrentUser
) -> SiteResponse | HTTPException:
    """
    Create a new Site.
    """
    logger = logging.getLogger("POST sites/")
    try:
        site = crud.create_site(db=session, site_input=site_in, user_id=current_user.id)
    except ValidationError as e:
        logger.info(e)
        raise HTTPException(status_code=422, detail="Bad body format")
    return site


@router.patch("/{site_id}", response_model=SiteResponse)
async def update_a_site(
    *,
    session: deps.SessionDep,
    site_id: int,
    site_in: SiteUpdate,
    current_user: deps.CurrentUser
) -> SiteResponse | HTTPException:
    """
    Update a Site.
    """
    logger = logging.getLogger("PATCH sites/")
    site = session.get(Site, site_id)

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    if site.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        site = crud.update_site(db=session, db_site=site, site_new_input=site_in)
    except ValidationError as e:
        logger.info(e)
        raise HTTPException(status_code=422, detail="Bad body format")
    return site


@router.delete("/{site_id}", response_model=DefaultResponseMessage)
async def delete_a_site(
    *,
    session: deps.SessionDep,
    site_id: int,
    current_user: deps.CurrentUser
) -> DefaultResponseMessage | HTTPException:
    """
    Delete a Site.
    """
    logger = logging.getLogger("DELETE sites/")
    site = session.get(Site, site_id)

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    if site.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    crud.delete_site(db=session, site=site)
    return DefaultResponseMessage(message="Site deleted successfully")

