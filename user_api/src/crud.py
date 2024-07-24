from datetime import datetime, timedelta

from sqlmodel import Session, select

from .models import (
    User,
    UserUpdate,
    UserCreate,
    Site,
    SiteCreate,
    SiteUpdate,
    Device,
    DeviceCreate,
    DeviceUpdate,
    Message,
)
from .core.security import get_password_hash


# -------------------------- USER -----------------------------------
def create_user(*, db: Session, user_input: UserCreate) -> User:
    user = User.model_validate(
        user_input, update={"hashed_password": get_password_hash(user_input.password)}
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(*, db: Session, db_user: User, user_new_input: UserUpdate) -> User:
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


# -------------------------- SITE -----------------------------------
def create_site(*, db: Session, site_input: SiteCreate, user_id: int) -> Site:
    site = Site.model_validate(site_input, update={"user_id": user_id})
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


def update_site(*, db: Session, db_site: Site, site_new_input: SiteUpdate) -> Site:
    site_data = site_new_input.model_dump(exclude_unset=True)
    db_site.sqlmodel_update(site_data)
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site


def get_site_by_name(*, db: Session, name: str) -> Site | None:
    statement = select(Site).where(Site.name == name)
    session_site = db.exec(statement).first()
    return session_site


def get_sites_by_user_id(*, db: Session, user_id: int) -> list[Site]:
    statement = select(Site).where(Site.user_id == user_id)
    session_sites = db.exec(statement).all()
    return session_sites


def delete_site(*, db: Session, site: Site) -> None:
    db.delete(site)
    db.commit()


def delete_sites_from_user(*, db: Session, user_id: int) -> None:
    statement = select(Site).where(Site.user_id == user_id)
    session_sites = db.exec(statement).all()
    for site in session_sites:
        db.delete(site)
    db.commit()


# -------------------------- DEVICE -----------------------------------
def create_device(*, db: Session, device_input: DeviceCreate) -> Device:
    device = Device.model_validate(device_input)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(*, db: Session, db_device: Device, device_new_input: DeviceUpdate) -> Device:
    device_data = device_new_input.model_dump(exclude_unset=True)
    db_device.sqlmodel_update(device_data)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device_by_name(*, db: Session, name: str) -> Device | None:
    statement = select(Device).where(Device.name == name)
    session_device = db.exec(statement).first()
    return session_device


def get_devices_by_type(*, db: Session, type: str, user_id: int) -> list[Device]:
    statement = select(Device).where(Device.type == type, Device.user_id == user_id)
    session_devices = db.exec(statement).all()
    return session_devices


def get_devices_by_model(*, db: Session, model: str, user_id: int) -> list[Device]:
    statement = select(Device).where(Device.model == model, Device.user_id == user_id)
    session_devices = db.exec(statement).all()
    return session_devices


def get_devices_by_user_id(*, db: Session, user_id: int) -> list[Device]:
    statement = select(Device).where(Device.user_id == user_id)
    session_devices = db.exec(statement).all()
    return session_devices


def get_devices_by_site_id(*, db: Session, site_id: int) -> list[Device]:
    statement = select(Device).where(Device.site_id == site_id)
    session_devices = db.exec(statement).all()
    return session_devices


def delete_devices_from_user(*, db: Session, user_id: int) -> None:
    statement = select(Device).where(Device.user_id == user_id)
    session_devices = db.exec(statement).all()
    for device in session_devices:
        db.delete(device)
    db.commit()


def delete_devices_per_site_id(*, db: Session, site_id: int) -> None:
    statement = select(Device).where(Device.site_id == site_id)
    session_devices = db.exec(statement).all()
    for device in session_devices:
        db.delete(device)
    db.commit()


def delete_device(*, db: Session, device: Device) -> None:
    db.delete(device)
    db.commit()


# -------------------------- MESSAGE -----------------------------------
def get_message_by_id(*, db: Session, message_id: int) -> Message | None:
    statement = select(Message).where(Message.id == message_id)
    session_message = db.exec(statement).first()
    return session_message


def get_messages(
        *, db: Session,
        device_id: int,
        start_date: str = datetime.now() - timedelta(hours=24),
        end_date: str = datetime.now() + timedelta(hours=1),
        limit: int = 100,
        offset: int = 0
) -> list[Message]:
    """
    By Period and Device ID
    Defaut: Period of 24 hours
    Format: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
    """
    statement = select(Message).where(
        Message.device_id == device_id,
        Message.created_on >= start_date.strftime('%Y-%m-%d %H:%M:%S'),
        Message.created_on <= end_date.strftime('%Y-%m-%d %H:%M:%S')
    ).offset(offset).limit(limit)
    session_messages = db.exec(statement).all()
    return session_messages


def delete_message(*, db: Session, message: Message) -> bool:
    db.delete(message)
    db.commit()
    return True


def delete_messages_list(*, db: Session, message_ids: list[int]) -> None:
    for message_id in message_ids:
        statement = select(Message).where(Message.id == message_id)
        message = db.exec(statement).first()
        if message:
            db.delete(message)
    db.commit()


def delete_messages_by_period(
        *, db: Session,
        device_id: int,
        start_date: str = datetime.now() - timedelta(hours=24),
        end_date: str
) -> None:
    """
    By Period and Device ID
    Defaut: Period of 24 hours
    Format: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
    """
    statement = select(Message).where(
        Message.device_id == device_id,
        Message.created_on >= start_date,
        Message.created_on <= end_date
    )
    session_messages = db.exec(statement).all()
    for message in session_messages:
        db.delete(message)
    db.commit()
