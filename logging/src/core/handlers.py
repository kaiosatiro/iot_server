# This module contains the "business logic" of the logging service.
# It is responsible for handling the log messages pulled from the queue.
from logging import getLogger

from src.config import settings
from src.core.abs import DB, DataManager, HandlerABC, SingletonMetaHandler
from src.core.data import get_data_manager

logger = getLogger(__name__)


class HandlerManager(HandlerABC, metaclass=SingletonMetaHandler):
    def __init__(self) -> None:
        self.db_manager: DataManager = get_data_manager()
        self.handlers: dict[str, HandlerABC] = {}

        self.instantiate_handlers()

    def instantiate_handlers(self) -> None:
        logger.info("Instantiating handlers")
        self.handlers = {
            settings.HANDLER_ID: Handler(
                origin=settings.HANDLER_ID,
                db_local=self.db_manager.get_local(),
                db_remote=self.db_manager.get_remote(),
            ),
            settings.RECEIVER_ID: Handler(
                origin=settings.RECEIVER_ID,
                db_local=self.db_manager.get_local(),
                db_remote=self.db_manager.get_remote(),
            ),
            settings.USERAPI_ID: Handler(
                origin=settings.USERAPI_ID,
                db_local=self.db_manager.get_local(),
                db_remote=self.db_manager.get_remote(),
            ),
            "UNKNOWN": Handler(
                origin="UNKNOWN",
                db_local=self.db_manager.get_local(),
                db_remote=self.db_manager.get_remote(),
            ),
        }

    def handle_message(self, msg: str | bytes, app_id: str) -> None:
        # logger.debug("Handling message: %s", msg)
        match app_id:
            case settings.HANDLER_ID:
                self.handlers[app_id].handle_message(msg)
            case settings.RECEIVER_ID:
                self.handlers[app_id].handle_message(msg)
            case settings.USERAPI_ID:
                self.handlers[app_id].handle_message(msg)
            case _:
                logger.warning("Unknown app_id: %s", app_id)
                self.handlers["UNKNOWN"].handle_message(msg)


def get_handlers_manager() -> HandlerABC:
    return HandlerManager()


class Handler(HandlerABC):
    def __init__(self, origin: str, db_local: DB, db_remote: DB | None = None) -> None:
        logger.info("Initializing handler for %s", origin)

        self.origin = origin
        self.db_local = db_local
        self.db_remote = db_remote

        self.db_local.set_origin(self.origin)

    def handle_message(self, msg: str | bytes) -> None:
        logger.debug("Handling message: %s", msg)
        body = msg.decode("utf-8") if isinstance(msg, bytes) else msg
        self.db_local.save(body)
        if self.db_remote:
            self.db_remote.save(body)
