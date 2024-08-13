import json
import logging
from time import sleep
from typing import Any

import pika  # type: ignore

import src.core.manager as manager
from src.config import settings
from src.core.abs import ABSQueueChannel


class MessageChannel(ABSQueueChannel):
    def __init__(self) -> None:
        self._connection: manager.PublishingManager
        self._channel: ABSQueueChannel
        self._exchange = settings.MESSAGES_EXCHANGE
        self._queue = settings.MESSAGES_QUEUE
        self._routing_key = settings.MESSAGES_ROUTING_KEY
        self._declare_exchange = settings.MESSAGES_DECLARE_EXCHANGE

        self.logger = logging.getLogger(self.__class__.__name__)

        self.connect()
        if self._connection.status() and self._declare_exchange:
            self.setup()

    def connect(self) -> None:
        self.logger.info("Connecting to Queue")
        self._connection = manager.get_queue_access()
        sleep(1)

        self.logger.info("Opening Channel")
        self._channel = self._connection.open_channel(tag=self.__class__.__name__)
        sleep(1)

    def status(self) -> bool:
        try:
            if self._channel.is_open:
                return True
        except AttributeError as e:
            self.logger.error(f"Error checking status: {e}")
        return False

    def stop(self) -> None:
        self._channel.close()

    def setup(self) -> None:
        self.logger.info(f"Connecting to {self._exchange} exchange")
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type="topic",
            durable=True,
        )

        self.logger.info(f"Connecting to {self._queue} queue")
        self._channel.queue_declare(
            queue=self._queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        self.logger.info(
            f"Binding {self._queue} to {self._exchange} with {self._routing_key}"
        )
        self._channel.queue_bind(
            exchange=self._exchange,
            queue=self._queue,
            routing_key=self._routing_key,
        )

    def publish_message(
        self, message: dict[Any, Any], content_type: str = "text/plain"
    ) -> None:
        properties = pika.BasicProperties(
            app_id="receiver",
            content_type=content_type,
            delivery_mode=2,
        )
        body = json.dumps(message)
        self.logger.info(
            f"Publishing message to exchange {self._exchange} with routing key {self._routing_key}"
        )
        self._connection.publish(
            self._channel.basic_publish(
                exchange=self._exchange,
                routing_key=self._routing_key,
                body=body,
                properties=properties,
                mandatory=True,
            )
        )
        self.logger.info("Message processed")

    def configure(
        self,
        exchange: str,
        queue: str | None = None,
        routing_key: str | None = None,
        declare_exchange: bool = False,
    ) -> None:
        # Configure the exchange, queue, and routing key, setup if _declare_exchange is True
        self._exchange = exchange
        self._queue = queue if queue else ""
        self._routing_key = routing_key if routing_key else "log"
        self._declare_exchange = declare_exchange

        if self._declare_exchange and self.status():
            self.setup()


def get_message_channel() -> MessageChannel:
    return MessageChannel()
