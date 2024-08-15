# This module contains the "business logic" of the logging service.
# It is responsible for handling the log messages pulled from the queue.
from logging import getLogger

from src.core.abs import HandlerABC, SingletonMetaHandler
from src.core.data import DataManager, DB, get_data_manager
from src.config import settings


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
        }

    def handle_message(self, msg: str | bytes, app_id: str, *args, **kwargs) -> None:
        logger.debug(f"Handling message: {msg}")
        match app_id:
            case settings.HANDLER_ID:
                self.handlers[app_id].handle_message(msg)
            case settings.RECEIVER_ID:
                self.handlers[app_id].handle_message(msg)
            case settings.USERAPI_ID:
                self.handlers[app_id].handle_message(msg)
            case _:
                logger.warning(f"Unknown app_id: {app_id}")


def get_handlers_manager() -> HandlerABC:
    return HandlerManager()


class Handler(HandlerABC):
    def __init__(
        self,
        origin: str,
        db_local: DB,
        db_remote: DB | None = None
    ) -> None:
        logger.info(f"Initializing handler for {origin}")

        self.origin = origin
        self.db_local = db_local
        self.db_remote = db_remote

        self.db_local.set_origin(self.origin)

    def handle_message(self, msg) -> None:
        logger.debug(f"Handling message: {msg}")
        self.db_local.save(msg)
