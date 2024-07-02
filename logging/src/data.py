# This module is responsible for saving data to a local or remote database.

from __future__ import annotations
from abc import ABC, abstractmethod

from logging import getLogger


logger = getLogger(__name__)


class DB(ABC):
    @abstractmethod
    def save(self, data, *args, **kwargs):
        pass


class DBManager(ABC):
    @abstractmethod
    def get_local(self) -> DB:
        pass

    @abstractmethod
    def get_remote(self) -> DB:
        pass


class DataSaverManager(DBManager):    
    def get_local(self) -> DB:
        return LocalSaver()
    
    def get_remote(self) -> DB:
        return RemoteSaver()


class LocalSaver(DB):
    def save(self, data, origin='Unknown'):
        logger.debug(f"Saving data locally: {data}")
        with open("src/logs/log.txt", "a") as f: # TODO: Change this to a environment variable path
            f.write(f"{origin}: {data.decode('utf-8')}\n")
                

class RemoteSaver(DB):
    def save(self, data):
        logger.debug(f"Saving data remotely: {data}")


def get_db_manager() -> DB:
    return DataSaverManager()
