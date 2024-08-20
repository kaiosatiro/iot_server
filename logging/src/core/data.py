# This module is responsible for saving data to a local or remote database.
import logging
from datetime import datetime

from src.config import settings
from src.core.abs import DB, DataManager
from src.core.time_service import get_time_service

logger = logging.getLogger(__name__)


# DB Object Factory
class Manager(DataManager):
    def get_local(self) -> DB:
        return LocalData()

    def get_remote(self) -> DB:
        return RemoteData()


def get_data_manager() -> DataManager:
    return Manager()


class LocalData(DB):
    def __init__(self) -> None:
        self.origin: str = ""
        self.path: str = settings.LOG_INFO_LOCAL_PATH
        self.datetime_service: object = get_time_service()

    def save(self, data: str) -> None:
        # logger.debug("Saving data locally: %s", data)
        date = self.datetime_service.get_current_date()  # type: ignore
        # data = data.decode("utf-8") if isinstance(data, bytes) else data
        with open(
            f"{self.path}{date}_{self.origin}.log", "a"
        ) as f:  # TODO: NEED to add size control here
            f.write(f"{data}\n")

    def set_current_date(self) -> None:
        logger.debug("Setting current date")
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    def set_origin(self, origin: str) -> None:
        logger.info("Setting origin: %s", origin)
        self.origin = origin


class RemoteData(DB):
    def save(self, data: str) -> None:
        logger.debug("Saving data remotely: %s", data)
        pass

    def set_origin(self, origin: str) -> None:
        pass
