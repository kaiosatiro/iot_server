# This module contains the "business logic" of the logging service. 
# It is responsible for handling the log messages pulled from the queue.

from __future__ import annotations
from abc import ABC, abstractmethod

from src.data import DBManager, DB

from logging import getLogger

logger = getLogger(__name__)


class Handler(ABC):
    @abstractmethod
    def handle_message(self, msg, properties) -> None:
        pass
    

class HandlerManager(Handler):
    def __init__(self, db_manager = DBManager | None):
        self.db_manager = db_manager
        if db_manager is None:
            logger.error("DBManager object is required")
            raise ValueError("DBManager object is required")
        
        self.handlers = {
            "logs_iot": HandlerLogsIoT( #TODO strongly cople, and data hardcoded, must be refactored to config files maybe?
                db_local=self.db_manager.get_local(),
                # db_remote=self.db_manager.get_remote()
            )
        }
    
    def handle_message(self, msg, properties):
        # logger.debug(f"Handling message: {msg}")
        self.handlers["logs_iot"].handle_message(msg.decode('utf-8'))


class HandlerLogsIoT(Handler):
    def __init__(
        self,
        db_local: DB | None,
        db_remote: DB | None = None
    ):
        self.db_local = db_local
        self.db_remote = db_remote

        self.db_local.set_origin("IoTSERVICES")

    def handle_message(self, msg):
        # logger.debug(f"Handling message: {msg}")
        self.db_local.save(msg)


class HandlerLogsDashboard(Handler):
    def __init__(
        self,
        db_local: DB | None,
    ):
        self.db_local = db_local
        self.db_local.set_origin("USERDASHBOARD")

    def handle_message(self, msg):
        # logger.debug(f"Handling message: {msg}")
        self.db_local.save(msg)


def get_handler(db) -> Handler:
    return HandlerManager(db)
