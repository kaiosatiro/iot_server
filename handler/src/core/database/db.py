from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

from src.core.database.engine import engine


Base = declarative_base()
Base.metadata.reflect(engine)


class Message(Base):  # type: ignore
    __table__ = Base.metadata.tables["message"]


class Device(Base):  # type: ignore
    __table__ = Base.metadata.tables["device"]


class Site(Base):  # type: ignore
    __table__ = Base.metadata.tables["site"]


class User(Base):  # type: ignore
    __table__ = Base.metadata.tables["user"]


class DB:
    def __init__(self) -> None:
        self.session: Session = Session(engine)
        self.active_devices: set = set()  # A 'cache' of active devices

        self._get_devices()

    def _get_devices(self) -> None:
        query = self.session.query(Device)
        self.active_devices = {device.id for device in query}

    def verify_device_id(self, device_id: int) -> bool:
        if device_id in self.active_devices:
            return True
        else:
            query = self.session.query(Device).filter(Device.id == device_id)
            if query.first():
                self.active_devices.add(device_id)
                return True
            return False

    def save_message(self, body: dict, device_id: int) -> None:
        message = Message(message=body, device_id=device_id)
        self.session.add(message)
        self.session.commit()

    def close(self) -> None:
        self.session.close()


def get_data_manager() -> DB:
    return DB()