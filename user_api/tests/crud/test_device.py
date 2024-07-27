from sqlmodel import Session

from src import crud
from src.models import DeviceCreate, DeviceUpdate, SiteCreate, UserCreate
from tests.utils import random_lower_string


def test_create_device(db: Session, userfix: dict, sitefix: dict, devicefix) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
    device = crud.create_device(db=db, device_input=device_in)

    assert device.name == device_in.name, "Device name does not match"
    assert device.model == device_in.model, "Device model does not match"
    assert device.type == device_in.type, "Device type does not match"
    assert (
        device.description == device_in.description
    ), "Device description does not match"
    assert device.user_id == user.id, "Device user_id does not match"
    assert device.site_id == site.id, "Device site_id does not match"
    assert device.created_on is not None, "Device created_on is None"


def test_update_device(db: Session, userfix: dict, sitefix: dict, devicefix) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
    device = crud.create_device(db=db, device_input=device_in)

    device_update = DeviceUpdate(
        name=random_lower_string(), description=random_lower_string()
    )
    device = crud.update_device(db=db, db_device=device, device_new_input=device_update)

    assert device.name == device_update.name, "Device name does not match"
    assert (
        device.description == device_update.description
    ), "Device description does not match"
    assert device.user_id == user.id, "Device user_id does not match"
    assert device.site_id == site.id, "Device site_id does not match"
    assert device.created_on is not None, "Device created_on is None"

    assert device.model == device.model, "Device model does not match"
    assert device.type == device.type, "Device type does not match"


def test_get_device_by_name(
    db: Session, userfix: dict, sitefix: dict, devicefix
) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
    device = crud.create_device(db=db, device_input=device_in)

    device_seek = crud.get_device_by_name(db=db, name=devicefix["name"])

    assert device_seek
    assert device_seek.name == device.name, "Device name does not match"
    assert device_seek.model == device.model, "Device model does not match"
    assert device_seek.type == device.type, "Device type does not match"
    assert (
        device_seek.description == device.description
    ), "Device description does not match"
    assert device_seek.user_id == user.id, "Device user_id does not match"
    assert device_seek.site_id == site.id, "Device site_id does not match"
    assert device_seek.created_on is not None, "Device created_on is None"


def test_get_device_by_name_none(db: Session, devicefix) -> None:
    device_seek = crud.get_device_by_name(db=db, name=devicefix["name"])

    assert not device_seek
    assert device_seek is None, f"device_seek: {device_seek}"


def test_get_devices_by_type(
    db: Session, userfix: dict, sitefix: dict, devicefix
) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    for _ in range(5):
        device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_type(db=db, type=devicefix["type"], user_id=user.id)

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.type == devicefix["type"], f"device: {device}"
        assert device.user_id == user.id, f"device: {device}"
        assert device.site_id == site.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_get_devices_by_model(
    db: Session, userfix: dict, sitefix: dict, devicefix
) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    for _ in range(5):
        device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_model(
        db=db, model=devicefix["model"], user_id=user.id
    )

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.model == devicefix["model"], f"device: {device}"
        assert device.user_id == user.id, f"device: {device}"
        assert device.site_id == site.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_get_devices_by_user_id(
    db: Session, userfix: dict, sitefix: dict, devicefix
) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    for _ in range(5):
        device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_user_id(db=db, user_id=user.id)

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.user_id == user.id, f"device: {device}"
        assert device.site_id == site.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_get_devices_by_site_id(
    db: Session, userfix: dict, sitefix: dict, devicefix
) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    for _ in range(5):
        device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
        device = crud.create_device(db=db, device_input=device_in)

    devices = crud.get_devices_by_site_id(db=db, site_id=site.id)

    assert len(devices) == 5, f"devices: {devices}"
    for device in devices:
        assert device.user_id == user.id, f"device: {device}"
        assert device.site_id == site.id, f"device: {device}"
        assert device.created_on is not None, f"device: {device}"


def test_delete_devices_from_user(
    db: Session, userfix: dict, sitefix: dict, devicefix
) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    for _ in range(5):
        device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
        crud.create_device(db=db, device_input=device_in)

    assert len(crud.get_devices_by_user_id(db=db, user_id=user.id)) == 5

    crud.delete_devices_from_user(db=db, user_id=user.id)

    devices = crud.get_devices_by_user_id(db=db, user_id=user.id)
    assert len(devices) == 0, f"devices: {devices}"


def test_delete_devices_per_site_id(
    db: Session, userfix: dict, sitefix: dict, devicefix
) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    for _ in range(5):
        device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
        crud.create_device(db=db, device_input=device_in)

    assert len(crud.get_devices_by_site_id(db=db, site_id=site.id)) == 5

    crud.delete_devices_per_site_id(db=db, site_id=site.id)

    devices = crud.get_devices_by_site_id(db=db, site_id=site.id)
    assert len(devices) == 0, f"devices: {devices}"


def test_delete_device(db: Session, userfix: dict, sitefix: dict, devicefix) -> None:
    user_in = UserCreate(**userfix)
    site_in = SiteCreate(**sitefix)
    user = crud.create_user(db=db, user_input=user_in)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    device_in = DeviceCreate(**devicefix, user_id=user.id, site_id=site.id)
    device = crud.create_device(db=db, device_input=device_in)

    assert crud.get_device_by_name(db=db, name=devicefix["name"])

    crud.delete_device(db=db, device=device)

    assert not crud.get_device_by_name(db=db, name=devicefix["name"])
    assert crud.get_devices_by_user_id(db=db, user_id=user.id) == []
