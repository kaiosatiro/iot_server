import logging
from typing import Annotated, Any

from asgi_correlation_id import correlation_id
from fastapi import Depends

from src.publishers.channels import MessageChannel, get_message_channel

logger = logging.getLogger("MessageHandler")


class MessageHandler:
    def __init__(self) -> None:
        self._channel: MessageChannel = get_message_channel()

        # self.connect()
        # if self._connection.status() and self._declare_exchange:
        #     self.setup()

    def _create_headers(self, device_id: int) -> dict[Any, Any]:
        return {
            "device_id": device_id,
        }

    def process_message(self, device_id: int, body: dict[Any, Any]) -> None:
        logger.info("Processing message for device %d", device_id)
        try:
            headers = self._create_headers(device_id)
            body.update(headers)
            self._channel.publish_message(
                body,
                correlation_id=correlation_id.get() or "",
                content_type="application/json",
            )
        except AttributeError as e:
            logger.error("Error publishing message: %s", e)
        except Exception as e:
            logger.error("Error processing message: %s", e)


def get_handler() -> MessageHandler:
    return MessageHandler()


message_handler = Annotated[MessageHandler, Depends(get_handler)]
