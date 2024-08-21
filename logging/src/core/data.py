# This module is responsible for saving data to a local or remote database.
import logging
import os
from io import TextIOWrapper

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
        self.datetime_service: object = (
            get_time_service()
        )  # TODO: Change it for the callable
        self.stream: TextIOWrapper | None = None
        self.basefilename: str = ""
        self.max_bytes: int = settings.LOG_FILE_MAX_SIZE
        self.backup_count: int = settings.LOG_FILE_BACKUP_COUNT

    def set_origin(self, origin: str) -> None:
        logger.info("Setting origin: %s", origin)
        self.origin = origin

    def save(self, data: str) -> None:
        logger.debug("Saving data locally: %s", data)
        date = self.datetime_service.get_current_date()  # type: ignore
        self.basefilename = os.path.join(self.path, f"{date}_{self.origin}.log")

        try:
            self.stream = self._open()
            if self.should_rollover(data):
                self.do_rollover()
            self.stream.write(data + "\n")

        except (
            Exception
        ) as e:  # try catch here we may lose msg because it will be acknoledged??
            logger.error("Error saving data: %s", e)
        finally:
            self.stream.flush()

    def should_rollover(self, data: str) -> bool:
        if self.stream is None:
            self.stream = self._open()
        if self.max_bytes > 0:
            if self.stream.tell() + len(data) >= self.max_bytes:
                return True
        return False

    def do_rollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None

        if self.backup_count > 0:
            for i in range(self.backup_count - 1, 0, -1):
                sfn = f"{self.basefilename}.{i}"
                dfn = f"{self.basefilename}.{i + 1}"
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)

            dfn = self.basefilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)

            if os.path.exists(self.basefilename):
                os.rename(self.basefilename, dfn)

        self.stream = self._open()

    def _open(self) -> TextIOWrapper:
        return open(self.basefilename, "a")


class RemoteData(DB):
    def save(self, data: str) -> None:
        logger.debug("Saving data remotely: %s", data)
        pass

    def set_origin(self, origin: str) -> None:
        pass
