import json
import logging
from time import sleep
from typing import Any

import pika  # type: ignore
from pika.channel import Channel  # type: ignore
from pika.spec import Basic, BasicProperties  # type: ignore

from src.queues.manager import PublishingManager, get_queue_access
from src.core.config import settings
from src.queues.abs import ABSQueueChannel  # ABSQueueConnectionManager


class LogChannel(ABSQueueChannel):
    def __init__(self) -> None:
        self._connection: PublishingManager
        self._channel: Channel
        self._exchange: str = settings.LOGGING_EXCHANGE
        self._queue: str = settings.LOG_QUEUE
        self._routing_key: str = settings.LOG_ROUTING_KEY

    def connect(self) -> None:
        self._connection = get_queue_access()
        sleep(1)
        self._channel = self._connection.open_channel(tag=self.__class__.__name__)
        sleep(1)

    def status(self) -> bool:
        try:
            if self._channel.is_open:
                return True
        except AttributeError as e:
            logging.getLogger(self.__class__.__name__).error(
                f"Error checking status: {e}"
            )
        return False

    def stop(self) -> None:
        self._channel.close()

    def setup(self) -> None:
        self._channel.exchange_declare(
            exchange=self._exchange,
            exchange_type="topic",
            durable=True,
        )
        self._channel.queue_declare(
            queue=self._queue,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
        self._channel.queue_bind(
            exchange=self._exchange,
            queue=self._queue,
            routing_key=self._routing_key,
        )

    def publish(self, message: str, content_type: str = "text/plain") -> None:
        properties = pika.BasicProperties(
            app_id=settings.USERAPI_ID,
            content_type=content_type,  # TODO: ADD to self
            delivery_mode=2,
        )
        self._connection.publish(
            self._channel.basic_publish(
                exchange=self._exchange,
                routing_key=self._routing_key,
                body=message,
                properties=properties,
                mandatory=True,
            )
        )


def get_log_channel() -> LogChannel:
    return LogChannel()


class RpcChannel:
    def __init__(self) -> None:
        self._connection: PublishingManager
        self._channel: Channel
        self._routing_key = settings.RPC_ROUTING_KEY

        self.response: str | None = None
        self.corr_id: str = ""
        self.callback_queue: str = ""

        self.logger = logging.getLogger(self.__class__.__name__)

        self.connect()
        if self._connection.status():
            self.setup()

    def connect(self) -> None:
        self.logger.info("Connecting to Queue")
        self._connection = get_queue_access()
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
        self._channel = self._connection.open_channel(tag=self.__class__.__name__)

        result = self._channel.queue_declare(
            queue="",
            exclusive=True,
        )
        self.callback_queue = result.method.queue

        self._channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        self.logger.info("rpc channel setup | queue: %s", self.callback_queue)

    def publish(
        self,
        message: dict[Any, Any],
        correlation_id: str,
    ) -> str | None:
        self.response = None
        self.corr_id = correlation_id

        properties = pika.BasicProperties(
            app_id=settings.USERAPI_ID,
            content_type="text/bytes",
            delivery_mode=2,
            correlation_id=correlation_id,
            reply_to=self.callback_queue,
        )

        body = json.dumps(message)
        self._connection.publish(
            self._channel.basic_publish(
                exchange="",
                routing_key=self._routing_key,
                body=body.encode(),
                properties=properties,
            )
        )
        self.logger.info(
            "RPC request to %s %s", message["method"], message["device_id"]
        )

        timeout = settings.RPC_TIMEOUT  # Set the timeout to 3 seconds
        while self.response is None and timeout > settings.RPC_TIMEOUT:
            self._connection._connection.process_data_events(time_limit=1)
            timeout -= 1

        if self.response is None:
            self.logger.error("RPC request timeout")

        return self.response

    def on_response(
        self,
        _unused_channel: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        self.logger.info(f"Received response. CorrID: {properties.correlation_id}")
        if self.corr_id == properties.correlation_id:
            self.response = body.decode()


def get_rpc_channel() -> RpcChannel:
    return RpcChannel()
