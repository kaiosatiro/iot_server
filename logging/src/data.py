# This module is responsible for saving data to a local or remote database.

from __future__ import annotations
from abc import ABC, abstractmethod

from os import getenv
from datetime import datetime

from logging import getLogger


logger = getLogger(__name__)


class DB(ABC):
    @abstractmethod
    def save(self, data, *args, **kwargs):
        pass
    
    @abstractmethod
    def set_origin(self, origin):
        pass


class DBManager(ABC):
    @abstractmethod
    def get_local(self) -> DB:
        pass

    @abstractmethod
    def get_remote(self) -> DB:
        pass

# DB Object Factory
class DataManager(DBManager):    
    def get_local(self) -> DB:
        return LocalData()
    
    def get_remote(self) -> DB:
        return RemoteData()


class LocalData(DB):
    def __init__(self, origin='Unknown'):
        self.path = LocalData.path_dir()
        self.current_date = datetime.now().strftime("%Y-%m-%d") #TODO: maybe a scheduler ?
        self.origin = origin
    
    def save(self, data):
        logger.debug(f"Saving data locally: {data}")
        with open(f"{self.path}{self.current_date}_{self.origin}.log", "a") as f: #TODO: NEED to add size control here
            f.write(f"{data}\n")
    
    def set_current_date(self):
        logger.debug("Setting current date")
        self.current_date = datetime.now().strftime("%Y-%m-%d")
    
    def set_origin(self, origin):
        logger.info(f"Setting origin: {origin}")
        self.origin = origin

    @staticmethod
    def path_dir():
        path = getenv("LOG_INFO_LOCAL_PATH")
        if path is None:
            return "/tmp/"
        return path
        

class RemoteData(DB):
    def save(self, data):
        logger.debug(f"Saving data remotely: {data}")
        pass

    def set_origin(self, origin):
        pass


def get_db_manager() -> DB:
    return DataManager()
