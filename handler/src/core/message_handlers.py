from logging import getLogger

from src.core.abs import Handler
from src.core.database.db import DB


class Message_Handler(Handler):
    def __init__(self) -> None:
        self.db_manager: DB = DB()
        self.logger = getLogger(__class__.__name__)

        self.logger.info("Message Handler initialized")

    def handle_message(self, body: str | bytes) -> None:
        self.logger.info(print(body))
        self.logger.info(print(type(body)))
        # body = json.loads(body.decode("utf-8"))
        self.logger.info(print(body))
        self.logger.info(print(type(body)))
        # device_id = body["device_id"]
        # correlation_id = body["correlation_id"]
        # self.logger.info("Handling message from device: %s", device_id, extra={"corrid": correlation_id})
        pass

    def close(self) -> None:
        self.db_manager.close()
        self.logger.info("Message Handler closed")


def get_handler() -> Message_Handler:
    return Message_Handler()
