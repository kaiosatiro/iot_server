import logging

from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool

import src.crud as crud
from src.core.config import settings
from src.models import (
    User,
    UserCreation,
)

engine = create_engine(
    str(settings.SQL_DATABASE_URI), poolclass=StaticPool
)  # TODO: try others poolclasses


def init_db(session: Session) -> None:
    from sqlmodel import SQLModel

    logger = logging.getLogger("init_db")
    logger.info("Creating database tables")
    SQLModel.metadata.create_all(engine)

    logger.info("Creating first superuser")
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
    ).first()

    if not user:
        user_in = UserCreation(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(db=session, user_input=user_in)
