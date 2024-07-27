import logging
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import func, select

import src.api.dependencies as deps
from src import crud
from src.models import (
    ResponseMessage,
    Site,
    SitePublic,
    SitesPublic,

)

router = APIRouter()


# @router.get("/", response_model=SitesPublic)
# def read_items(
#     session: deps.SessionDep, current_user: deps.CurrentUser, skip: int = 0, limit: int = 100
# ) -> Any:
#     """
#     Retrieve Sites.
#     """

#     if current_user.is_superuser:
#         # count_statement = select(func.count()).select_from(Site)
#         # count = session.exec(count_statement).one()
#         # statement = select(Item).offset(skip).limit(limit)
#         # items = session.exec(statement).all()
#     else:
#         # count_statement = (
#         #     select(func.count())
#         #     .select_from(Item)
#         #     .where(Item.owner_id == current_user.id)
#         # )
#         # count = session.exec(count_statement).one()
#         # statement = (
#         #     select(Item)
#         #     .where(Item.owner_id == current_user.id)
#         #     .offset(skip)
#         #     .limit(limit)
#         # )
#         # items = session.exec(statement).all()

#     return SitesPublic(data=items, count=count)
