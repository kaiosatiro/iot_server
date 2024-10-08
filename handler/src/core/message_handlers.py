from logging import getLogger
import json

from src.core.abs import Handler
from src.core.database.db import DB


class Message_Handler(Handler):
    def __init__(self) -> None:
        self.db: DB = DB()
        self.logger = getLogger(self.__class__.__name__)

        self.logger.info("Message Handler initialized")

    def handle_message(self, msg: str | bytes, corr_id: str) -> None:
        try:
            body = dict(
                json.loads(msg.decode("utf-8") if isinstance(msg, bytes) else msg)
            )
            device_id = int(body["device_id"])

            self.logger.info(
                "Handling message from device: %s",
                device_id,
                extra={"corrid": corr_id},
            )

            if self.db.verify_device_id(device_id):
                body.pop("device_id")
                self.db.save_message(body, device_id)
                self.logger.info("Message saved", extra={"corrid": corr_id})
            else:
                self.logger.warning("Device ID not found", extra={"corrid": corr_id})

        except Exception as e:
            self.logger.error(
                "Error handling message: %s", e, extra={"corrid": corr_id}
            )

    def handle_rpc_request(self, corr_id: str, request: bytes) -> str:
        self.logger.info("Handling RPC request", extra={"corrid": corr_id})
        self.logger.debug("Request body: %s", request, extra={"corrid": corr_id})
        try:
            body = dict(json.loads(request.decode("utf-8")))
            if body["method"] == "add":
                device_id = int(body["device_id"])
                self.db.add_device_to_cache(device_id)
                self.logger.info(
                    "Device added to cache: %s", device_id, extra={"corrid": corr_id}
                )

            elif body["method"] == "remove":
                device_id = int(body["device_id"])
                self.db.remove_device_from_cache(device_id)
                self.logger.info(
                    "Device removed from cache: %s",
                    device_id,
                    extra={"corrid": corr_id},
                )

        except Exception as e:
            self.logger.error(
                "Error handling RPC request: %s", e, extra={"corrid": corr_id}
            )
        finally:
            return "ok"

    def close(self) -> None:
        self.db.close()
        self.logger.info("Message Handler closed")


def get_handler() -> Message_Handler:
    return Message_Handler()
