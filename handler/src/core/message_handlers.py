from logging import getLogger
import json

from src.core.abs import Handler
from src.core.database.db import DB


class Message_Handler(Handler):
    def __init__(self) -> None:
        self.db: DB = DB()
        self.logger = getLogger(self.__class__.__name__)

        self.logger.info("Message Handler initialized")

    def handle_message(self, msg: str | bytes) -> None:
        try:
            body = dict(
                json.loads(msg.decode("utf-8") if isinstance(msg, bytes) else msg)
            )
            device_id = int(body["device_id"])
            correlation_id = body["correlation_id"]
            self.logger.info(
                "Handling message from device: %s",
                device_id,
                extra={"corrid": correlation_id},
            )

            if self.db.verify_device_id(device_id):
                self.db.save_message(body, device_id)
                self.logger.info("Message saved", extra={"corrid": correlation_id})
            else:
                self.logger.warning(
                    "Device ID not found", extra={"corrid": correlation_id}
                )

        except Exception as e:
            self.logger.error("Error handling message: %s", e)

    def close(self) -> None:
        self.db.close()
        self.logger.info("Message Handler closed")


def get_handler() -> Message_Handler:
    return Message_Handler()
