from sqlmodel import Session

from src import crud
from src.models import DeviceCreation, DeviceUpdate, EnvironmentCreation, UserCreation
from tests.utils import random_lower_string


def test_create_device(db: Session, userfix: dict, environmentfix: dict, devicefix) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
    device = crud.create_device(db=db, device_input=device_in)

    assert device.token
    assert device.name == device_in.name, "Device name does not match"
    assert device.model == device_in.model, "Device model does not match"
    assert device.type == device_in.type, "Device type does not match"
    assert (
        device.description == device_in.description
    ), "Device description does not match"
    assert device.owner_id == user.id, "Device owner_id does not match"
    assert device.environment_id == environment.id, "Device environment_id does not match"
    assert device.created_on is not None, "Device created_on is None"


def test_update_device(db: Session, userfix: dict, environmentfix: dict, devicefix) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
    device = crud.create_device(db=db, device_input=device_in)

    device_update = DeviceUpdate(
        name=random_lower_string(), description=random_lower_string()
    )
    device = crud.update_device(db=db, db_device=device, device_new_input=device_update)

    assert device.name == device_update.name, "Device name does not match"
    assert (
        device.description == device_update.description
    ), "Device description does not match"
    assert device.owner_id == user.id, "Device owner_id does not match"
    assert device.environment_id == environment.id, "Device environment_id does not match"
    assert device.created_on is not None, "Device created_on is None"

    assert device.model == device.model, "Device model does not match"
    assert device.type == device.type, "Device type does not match"


def test_get_device_by_name(
    db: Session, userfix: dict, environmentfix: dict, devicefix
) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
    device = crud.create_device(db=db, device_input=device_in)

    device_seek = crud.get_device_by_name(db=db, name=devicefix["name"])

    assert device_seek
    assert device_seek.name == device.name, "Device name does not match"
    assert device_seek.model == device.model, "Device model does not match"
    assert device_seek.type == device.type, "Device type does not match"
    assert (
        device_seek.description == device.description
    ), "Device description does not match"
    assert device_seek.owner_id == user.id, "Device owner_id does not match"
    assert device_seek.environment_id == environment.id, "Device environment_id does not match"
    assert device_seek.created_on is not None, "Device created_on is None"


def test_get_device_by_name_none(db: Session, devicefix) -> None:
    device_seek = crud.get_device_by_name(db=db, name=devicefix["name"])

    assert not device_seek
    assert device_seek is None, f"device_seek: {device_seek}"


def test_get_devices_by_type(
    db: Session, userfix: dict, environmentfix: dict, devicefix
) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    for _ in range(5):
        device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_type(db=db, type=devicefix["type"], owner_id=user.id)

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.type == devicefix["type"], f"device: {device}"
        assert device.owner_id == user.id, f"device: {device}"
        assert device.environment_id == environment.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_get_devices_by_model(
    db: Session, userfix: dict, environmentfix: dict, devicefix
) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    for _ in range(5):
        device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_model(
        db=db, model=devicefix["model"], owner_id=user.id
    )

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.model == devicefix["model"], f"device: {device}"
        assert device.owner_id == user.id, f"device: {device}"
        assert device.environment_id == environment.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_get_devices_by_owner_id(
    db: Session, userfix: dict, environmentfix: dict, devicefix
) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    for _ in range(5):
        device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_owner_id(db=db, owner_id=user.id)

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.owner_id == user.id, f"device: {device}"
        assert device.environment_id == environment.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_get_devices_by_environment_id(
    db: Session, userfix: dict, environmentfix: dict, devicefix
) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    for _ in range(5):
        device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_environment_id(db=db, environment_id=environment.id)

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.owner_id == user.id, f"device: {device}"
        assert device.environment_id == environment.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_delete_devices_from_user(
    db: Session, userfix: dict, environmentfix: dict, devicefix
) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    for _ in range(5):
        device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
        crud.create_device(db=db, device_input=device_in)

    assert len(crud.get_devices_by_owner_id(db=db, owner_id=user.id)) == 5

    crud.delete_devices_from_user(db=db, owner_id=user.id)

    devices = crud.get_devices_by_owner_id(db=db, owner_id=user.id)
    assert len(devices) == 0, f"devices: {devices}"


def test_delete_devices_per_environment_id(
    db: Session, userfix: dict, environmentfix: dict, devicefix
) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    for _ in range(5):
        device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
        crud.create_device(db=db, device_input=device_in)

    assert len(crud.get_devices_by_environment_id(db=db, environment_id=environment.id)) == 5

    crud.delete_devices_per_environment_id(db=db, environment_id=environment.id)

    devices = crud.get_devices_by_environment_id(db=db, environment_id=environment.id)
    assert len(devices) == 0, f"devices: {devices}"


def test_delete_device(db: Session, userfix: dict, environmentfix: dict, devicefix) -> None:
    user_in = UserCreation(**userfix)
    environment_in = EnvironmentCreation(**environmentfix)
    user = crud.create_user(db=db, user_input=user_in)
    environment = crud.create_environment(db=db, environment_input=environment_in, owner_id=user.id)

    device_in = DeviceCreation(**devicefix, owner_id=user.id, environment_id=environment.id)
    device = crud.create_device(db=db, device_input=device_in)

    assert crud.get_device_by_name(db=db, name=devicefix["name"])

    crud.delete_device(db=db, device=device)

    assert not crud.get_device_by_name(db=db, name=devicefix["name"])
    assert crud.get_devices_by_owner_id(db=db, owner_id=user.id) == []
