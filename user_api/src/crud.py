from sqlmodel import Session, select

from .models import UserUpdate, UserCreate, User
from .core.security import get_password_hash


# -------------------------- USER -----------------------------------
def create_user(*, db:Session, user_input:UserCreate) -> User:
    user = User.model_validate(
        user_input, update={"hashed_password": get_password_hash(user_input.password)}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(*, db:Session, db_user:User, user_new_input:UserUpdate) -> User:
    user_data = user_new_input.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(*, db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = db.exec(statement).first()
    return session_user

def deactivate_user(*, db: Session, user: User) -> User:
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_password(*, db: Session, user: User, password: str) -> User:
    hashed_password = get_password_hash(password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
