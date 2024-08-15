# This module is responsible for saving data to a local or remote database.
import logging
from datetime import datetime

from src.core.abs import DB, DataManager
from src.core.time_service import get_time_service
from src.config import settings


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
        self.origin: str = 'UNKNOWN'
        self.path: str = settings.LOG_INFO_LOCAL_PATH
        self.datetime_service: object = get_time_service()

    def save(self, data: str | bytes) -> None:
        logger.debug(f"Saving data locally: {data}")
        date = self.datetime_service.get_current_date()
        with open(f"{self.path}{date}_{self.origin}.log", "a") as f:  # TODO: NEED to add size control here
            f.write(f"{data}\n")

    def set_current_date(self) -> None:
        logger.debug("Setting current date")
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    def set_origin(self, origin: str) -> None:
        logger.info(f"Setting origin: {origin}")
        self.origin = origin


class RemoteData(DB):
    def save(self, data: str | bytes) -> None:
        logger.debug(f"Saving data remotely: {data}")
        pass

    def set_origin(self, origin: str) -> None:
        pass
