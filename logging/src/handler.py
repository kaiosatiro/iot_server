# This module contains the "business logic" of the logging service. 
# It is responsible for handling the log messages pulled from the queue.

from __future__ import annotations
from abc import ABC, abstractmethod

from data import DBManager, DB

from logging import getLogger

logger = getLogger(__name__)


class Handler(ABC):
    @abstractmethod
    def handle_message(self, msg) -> None:
        pass
    

class HandlerManager(Handler):
    def __init__(self, db_manager = DBManager | None):
        self.db_manager = db_manager
        if db_manager is None:
            logger.error("DBManager object is required")
            raise ValueError("DBManager object is required")
        
        self.handlers = {
            "logs_iot": HandlerLogsIoT(
                db_local=self.db_manager.get_local(),
                # db_remote=self.db_manager.get_remote()
            )
        }
    
    def handle_message(self, msg):
        # logger.debug(f"Handling message: {msg}")
        self.handlers["logs_iot"].handle_message(msg)


class HandlerLogsIoT(Handler):
    def __init__(
        self,
        db_local: DB | None,
        db_remote: DB | None = None
    ):
        self.db_local = db_local
        self.db_remote = db_remote

    def handle_message(self, msg):
        # logger.debug(f"Handling message: {msg}")
        self.db_local.save(msg, origin="IoTServices")


class HandlerLogsDashboard(Handler):
    def __init__(
        self,
        db_local: DB | None,
    ):
        self.db_local = db_local

    def handle_message(self, msg):
        # logger.debug(f"Handling message: {msg}")
        self.db_local.save(msg, origin="UserDashboard")


def get_handler_manager(db) -> Handler:
    return HandlerManager(db)
