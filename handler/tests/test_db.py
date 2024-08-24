from typing import Generator

from sqlalchemy.orm.session import Session
import pytest

from tests.conftest import create_test_data

from src.core.database.db import engine, DB, Message, Device, Site, User


class TestDB:
    @pytest.fixture()
    def session(self) -> Generator[Session, None, None]:
        with Session(engine, expire_on_commit=False) as session:
            create_test_data(session)
            yield session
            session.query(User).delete()
            session.query(Site).delete()
            session.query(Device).delete()
            session.query(Message).delete()
            session.commit()

    def test_get_devices_lenght(self, session: Session) -> None:
        db = DB()
        assert (
            len(db.active_devices) == 100
        ), "Active devices should be 100"  # Value set in conftest.py

    def test_check_device_exists_in_cache_by_id(self, session: Session) -> None:
        db = DB()
        id_ = session.query(Device).first()
        assert db.verify_device_id(id_.id), "Device should exist"

    def test_check_device_not_in_cache_but_in_db(self, session: Session) -> None:
        db = DB()
        id_ = session.query(Device).first()
        db.active_devices.remove(id_.id)
        assert db.verify_device_id(id_.id), "Device should exist"

    def test_check_device_not_in_cache_nor_db(self, session: Session) -> None:
        db = DB()
        id_ = session.query(Device).first()
        db.active_devices.remove(id_.id)
        session.query(Device).delete()
        session.commit()
        assert not db.verify_device_id(id_.id), "Device should not exist"

    # --- Save Message ---
    def test_save_message(self, session: Session) -> None:
        db = DB()
        device_id = session.query(Device).first().id
        message = {
            "device_id": 123,
            "timestamp": "2023-10-01T12:34:56",
            "data": {"temperature": 22.5, "humidity": 45},
        }
        db.save_message(message, device_id)
        assert session.query(Message).count() == 1, "Message should be saved"

    def test_add_device_to_cache(self, session: Session) -> None:
        db = DB()
        device_id = 123
        db.add_device_to_cache(device_id)
        assert device_id in db.active_devices, "Device should be added to cache"

    def test_remove_device_from_cache(self, session: Session) -> None:
        db = DB()
        device_id = 123
        db.active_devices.add(device_id)
        db.remove_device_from_cache(device_id)
        assert device_id not in db.active_devices, "Device should be removed from cache"
