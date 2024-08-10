import logging

from asgi_correlation_id import correlation_id

from src.publishers.abs import ABSQueueChannel
from src.publishers.channels import get_message_channel, MessageChannel


logger = logging.getLogger(__name__)


class MessageHandler:
    def __init__(
            self, channel: ABSQueueChannel = get_message_channel()
        ):
        self._channel: MessageChannel = channel

    def _create_headers(self, device_id: int) -> dict:
        return {
            "device_id": device_id,
            "request_id": correlation_id.get() or "",
        }
    
    def process_message(self, device_id: int, body: dict) -> None:
        logger.info("Processing message for device %d", device_id)
        try:
            headers = self._create_headers(device_id)
            self._channel.publish_message(headers, body, content_type="application/json")
        except Exception as e:
            logger.error("Error processing message: %s", e)
        finally:
            logger.info("Message processed")




        