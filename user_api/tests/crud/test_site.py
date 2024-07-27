from sqlmodel import Session

from src import crud
from src.models import (
    Site,
    SiteCreate,
    SiteUpdate,
    UserCreate,
)
from tests.utils import random_lower_string


def test_create_site(db: Session, userfix: dict, sitefix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    site_in = SiteCreate(**sitefix)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    assert (
        site.name == sitefix["name"]
    ), f"site.name: {site.name}, sitefix['name']: {sitefix['name']}"
    assert (
        site.description == sitefix["description"]
    ), f"site.description: {site.description}, sitefix['description']: {sitefix['description']}"
    assert site.user_id == user.id, f"site.user_id: {site.user_id}, user.id: {user.id}"


def test_update_site(db: Session, userfix: dict, sitefix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    site_in = SiteCreate(**sitefix)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)
    site_update = SiteUpdate(
        name=random_lower_string(),
    )
    site_seek = crud.update_site(db=db, db_site=site, site_new_input=site_update)

    assert (
        site_seek.name == site_update.name
    ), f"site_seek.name: {site_seek.name}, site_update.name: {site_update.name}"
    assert (
        site_seek.user_id == user.id
    ), f"site_seek.user_id: {site_seek.user_id}, user.id: {user.id}"
    assert site_seek.id == site.id, f"site_seek.id: {site_seek.id}, site.id: {site.id}"

    site_update2 = SiteUpdate(description=random_lower_string())
    site3 = crud.update_site(db=db, db_site=site, site_new_input=site_update2)

    assert (
        site3.description == site_update2.description
    ), f"site3.description: {site3.description}, site_update2.desc: {site_update2.description}"
    assert (
        site3.user_id == user.id
    ), f"site3.user_id: {site3.user_id}, user.id: {user.id}"


def test_get_site_by_name(db: Session, userfix: dict, sitefix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    site_in = SiteCreate(**sitefix)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)
    site_seek = crud.get_site_by_name(db=db, name=sitefix["name"])

    assert site_seek
    assert (
        site_seek.name == site.name
    ), f"site_seek.name: {site_seek.name}, site.name: {site.name}"
    assert (
        site_seek.description == site.description
    ), f"site_seek.description: {site_seek.description}, site.description: {site.description}"
    assert (
        site_seek.user_id == user.id
    ), f"site_seek.user_id: {site_seek.user_id}, user.id: {user.id}"
    assert site_seek.id == site.id, f"site_seek.id: {site_seek.id}, site.id: {site.id}"


def test_get_site_by_name_none(db: Session, sitefix: dict) -> None:
    site_seek = crud.get_site_by_name(db=db, name=sitefix["name"])
    assert not site_seek
    assert site_seek is None, f"site_seek: {site_seek}"


def test_get_sites_by_user_id(db: Session, userfix: dict, sitefix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    site_in = SiteCreate(**sitefix)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)
    site_seek = crud.get_sites_by_user_id(db=db, user_id=user.id)

    assert site_seek
    assert (
        site_seek[0].name == site.name
    ), f"site_seek[0].name: {site_seek[0].name}, site.name: {site.name}"
    assert (
        site_seek[0].description == site.description
    ), f"site_seek[0].description: {site_seek[0].description}, site.description: {site.description}"
    assert (
        site_seek[0].user_id == user.id
    ), f"site_seek[0].user_id: {site_seek[0].user_id}, user.id: {user.id}"
    assert (
        site_seek[0].id == site.id
    ), f"site_seek[0].id: {site_seek[0].id}, site.id: {site.id}"

    site_in = SiteCreate(**sitefix)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)
    site_seek = crud.get_sites_by_user_id(db=db, user_id=user.id)

    assert (
        site_seek[1].name == site.name
    ), f"site_seek[1].name: {site_seek[1].name}, site.name: {site.name}"
    assert (
        site_seek[1].description == site.description
    ), f"site_seek[1].description: {site_seek[1].description}, site.description: {site.description}"
    assert (
        site_seek[1].user_id == user.id
    ), f"site_seek[1].user_id: {site_seek[1].user_id}, user.id: {user.id}"
    assert (
        site_seek[1].id == site.id
    ), f"site_seek[1].id: {site_seek[1].id}, site.id: {site.id}"


def test_delete_site(db: Session, userfix: dict, sitefix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)
    site_in = SiteCreate(**sitefix)
    site = crud.create_site(db=db, site_input=site_in, user_id=user.id)

    site_seek = db.get(Site, site.id)

    assert site_seek
    assert (
        site_seek.name == site_in.name
    ), f"site_seek.name: {site_seek.name}, site_in.name: {site_in.name}"

    crud.delete_site(db=db, site=site)

    assert not db.get(Site, site.id), "site should be deleted"
    assert not crud.get_site_by_name(
        db=db, name=sitefix["name"]
    ), "site should be deleted"


def test_delete_sites_from_user(db: Session, userfix: dict, sitefix: dict) -> None:
    user_in = UserCreate(**userfix)
    user = crud.create_user(db=db, user_input=user_in)

    for _ in range(3):
        site_in = SiteCreate(**sitefix)
        crud.create_site(db=db, site_input=site_in, user_id=user.id)

    site_seek = crud.get_sites_by_user_id(db=db, user_id=user.id)
    site_seek_count = len(site_seek)

    assert site_seek_count == 3, f"site_seek_count: {site_seek_count}"

    crud.delete_sites_from_user(db=db, user_id=user.id)

    site_seek = crud.get_sites_by_user_id(db=db, user_id=user.id)

    assert not site_seek, f"site_seek: {site_seek}"
    assert site_seek == [], f"site_seek: {site_seek}"
