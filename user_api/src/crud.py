from collections.abc import Sequence
from datetime import datetime, timedelta

from sqlmodel import Session, select

import src.core.security as security
from src.utils import generate_random_number

from .models import (
    Device,
    DeviceCreation,
    DeviceUpdate,
    Environment,
    EnvironmentCreation,
    EnvironmentUpdate,
    Message,
    User,
    UserCreation,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)


# -------------------------- USER -----------------------------------
def create_user(*, db: Session, user_input: UserCreation | UserRegister) -> User:
    _id = generate_random_number(10000, 99999)
    while db.get(User, _id):
        _id = generate_random_number(10000, 99999)
    user = User.model_validate(
        user_input,
        update={
            "hashed_password": security.get_password_hash(user_input.password),
            "id": _id,
        },
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    *, db: Session, db_user: User, user_new_input: UserUpdate | UserUpdateMe
) -> User:
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


def get_user_by_username(*, db: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    session_user = db.exec(statement).first()
    return session_user


def deactivate_user(*, db: Session, user: User) -> User:
    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def activate_user(*, db: Session, user: User) -> User:
    user.is_active = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_password(*, db: Session, user: User, new_password: str) -> User:
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(*, db: Session, username: str, password: str) -> User | None:
    db_user = get_user_by_username(db=db, username=username)
    if not db_user:
        return None
    if not security.verify_password(password, db_user.hashed_password):
        return None
    return db_user


# -------------------------- ENVIRONMENT -----------------------------------
def create_environment(
    *, db: Session, environment_input: EnvironmentCreation, owner_id: int
) -> Environment:
    _id = generate_random_number(1000000, 9999999)
    while db.get(Environment, _id):
        _id = generate_random_number(1000000, 9999999)
    environment = Environment.model_validate(
        environment_input, update={"owner_id": owner_id, "id": _id}
    )
    db.add(environment)
    db.commit()
    db.refresh(environment)
    return environment


def update_environment(
    *,
    db: Session,
    db_environment: Environment,
    environment_new_input: EnvironmentUpdate,
) -> Environment:
    environment_data = environment_new_input.model_dump(exclude_unset=True)
    db_environment.sqlmodel_update(environment_data)
    db.add(db_environment)
    db.commit()
    db.refresh(db_environment)
    return db_environment


def get_environment_by_name(*, db: Session, name: str) -> Environment | None:
    statement = select(Environment).where(Environment.name == name)
    session_environment = db.exec(statement).first()
    return session_environment


def get_environments_by_owner_id(
    *, db: Session, owner_id: int
) -> Sequence[Environment]:
    statement = select(Environment).where(Environment.owner_id == owner_id)
    session_environments = db.exec(statement).all()
    return session_environments


def delete_environment(*, db: Session, environment: Environment) -> None:
    db.delete(environment)
    db.commit()


def delete_environments_from_user(*, db: Session, owner_id: int) -> None:
    statement = select(Environment).where(Environment.owner_id == owner_id)
    session_environments = db.exec(statement).all()
    for environment in session_environments:
        db.delete(environment)
    db.commit()


# -------------------------- DEVICE -----------------------------------
def create_device(*, db: Session, device_input: DeviceCreation) -> Device:
    _id = generate_random_number(1000000000, 2147483645)
    while db.get(Device, _id):
        _id = generate_random_number(1000000000, 2147483645)

    device = Device.model_validate(
        device_input,
        update={"id": _id, "token": security.create_device_access_token(_id)},
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(
    *, db: Session, db_device: Device, device_new_input: DeviceUpdate
) -> Device:
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


def get_devices_by_type(*, db: Session, type: str, owner_id: int) -> Sequence[Device]:
    statement = select(Device).where(Device.type == type, Device.owner_id == owner_id)
    session_devices = db.exec(statement).all()
    return session_devices


def get_devices_by_model(*, db: Session, model: str, owner_id: int) -> Sequence[Device]:
    statement = select(Device).where(Device.model == model, Device.owner_id == owner_id)
    session_devices = db.exec(statement).all()
    return session_devices


def get_devices_by_owner_id(*, db: Session, owner_id: int) -> Sequence[Device]:
    statement = select(Device).where(Device.owner_id == owner_id)
    session_devices = db.exec(statement).all()
    return session_devices


def get_devices_by_environment_id(
    *, db: Session, environment_id: int
) -> Sequence[Device]:
    statement = select(Device).where(Device.environment_id == environment_id)
    session_devices = db.exec(statement).all()
    return session_devices


def delete_devices_from_user(*, db: Session, owner_id: int) -> None:
    statement = select(Device).where(Device.owner_id == owner_id)
    session_devices = db.exec(statement).all()
    for device in session_devices:
        db.delete(device)
    db.commit()


def delete_devices_per_environment_id(*, db: Session, environment_id: int) -> None:
    statement = select(Device).where(Device.environment_id == environment_id)
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
    *,
    db: Session,
    device_id: int,
    start_date: str = str(datetime.now() - timedelta(hours=24)),
    end_date: str = str(datetime.now() + timedelta(hours=1)),
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Message]:
    """
    By Period and Device ID
    Defaut: Period of 24 hours
    Format:
        Complete: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
        Date: '2024-07-22' %Y-%m-%d,
    Limit: 100 messages, Default: 100
    """

    statement = (
        select(Message)
        .where(
            Message.device_id == device_id,
            Message.inserted_on >= start_date,
            Message.inserted_on <= end_date,
        )
        .offset(offset)
        .limit(limit)
    )
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
    *,
    db: Session,
    device_id: int,
    start_date: str = str(datetime.now() - timedelta(hours=24)),
    end_date: str,
) -> None:
    """
    By Period and Device ID
    Defaut: Period of 24 hours
    Format: '2024-07-22 13:00:44' %Y-%m-%d %H:%M:%S,
    """
    statement = select(Message).where(
        Message.device_id == device_id,
        Message.inserted_on >= start_date,
        Message.inserted_on <= end_date,
    )
    session_messages = db.exec(statement).all()
    for message in session_messages:
        db.delete(message)
    db.commit()


def delete_all_messages_per_device(*, db: Session, device_id: int) -> None:
    statement = select(Message).where(Message.device_id == device_id)
    session_messages = db.exec(statement).all()
    for message in session_messages:
        db.delete(message)
    db.commit()
