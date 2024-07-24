from sqlmodel import Session, create_engine, select
from sqlmodel.pool import StaticPool

from src.models import (
    User,
    UserCreate,
    )
import src.crud as crud
from src.core.config import settings


engine = create_engine(str(settings.SQL_DATABASE_URI), poolclass=StaticPool)

def init_db(session: Session) -> None:
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
    ).first()
    
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_NAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(db=session, user_input=user_in)




