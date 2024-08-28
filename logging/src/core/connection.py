import logging

from pika import (  # type: ignore
    BasicProperties,
    ConnectionParameters,
    PlainCredentials,
    SelectConnection,
)
from pika.adapters.base_connection import BaseConnection  # type: ignore
from pika.channel import Channel  # type: ignore
from pika.connection import Connection  # type: ignore
from pika.exchange_type import ExchangeType  # type: ignore
from pika.spec import Basic  # type: ignore

from src.config import settings
from src.core.abs import HandlerABC, SingletonConnection


class ConnectionManager(metaclass=SingletonConnection):
    EXCHANGE = settings.LOGGING_EXCHANGE
    EXCHANGE_TYPE = ExchangeType.topic
    QUEUE = settings.LOG_QUEUE
    ROUTING_KEY = settings.LOG_ROUTING_KEY

    def __init__(self, handler: HandlerABC | None = None) -> None:
        self._connection: BaseConnection = None
        self._channel: Channel = None
        self._consumer_tag: str = ""

        # ---
        self._handler: HandlerABC | None = handler
        # ---

        self._consuming: bool = False
        self._closing: bool = False

        self.should_reconnect: bool = False
        self.was_consuming: bool = False

        # TODO: In production, try higher prefetch values
        # for higher consumer throughput
        self._prefetch_count: int = 1

        self.logger = logging.getLogger(self.__class__.__name__)

    def close_connection(self) -> None:
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            self.logger.info("Connection is closing or already closed")
        else:
            self.logger.info("Closing connection")
            self._connection.close()

    # ----------------------------------------
    def connect(self) -> None:
        self.logger.info("Connecting to RabbitMQ server")

        parameters = ConnectionParameters(
            host=settings.RABBITMQ_DNS,
            port=settings.RABBITMQ_PORT,
            credentials=PlainCredentials(
                settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD
            ),
            heartbeat=3600,
        )

        self._connection = SelectConnection(
            parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed,
        )

    def on_connection_open(self, _unused_conn: Connection) -> None:
        self.logger.info("Connection opened")
        self.open_channel()

    def on_connection_open_error(
        self, _unused_conn: Connection, err: Exception
    ) -> None:
        self.logger.error("Connection open failed: %s", err)
        self.reconnect()

    def on_connection_closed(self, _unused_conn: Connection, reason: Exception) -> None:
        self.logger.warning("Connection closed: %s", reason)

        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning("Connection closed, reconnect necessary: %s", reason)
            self.reconnect()

    # ----------------------------------------
    def reconnect(self) -> None:
        self.should_reconnect = True
        self.stop()

    # ----------------------------------------
    def open_channel(self) -> None:
        self.logger.info("Creating a new channel")

        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel: Channel) -> None:
        self.logger.info("Channel opened")

        self._channel = channel
        self.setup_exchange()
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel: Channel, reason: Exception) -> None:
        self.logger.warning("Channel %i was closed: %s", channel, reason)

        self.close_connection()

    # ----------------------------------------
    def setup_exchange(self) -> None:
        self.logger.info("Declaring exchange '%s'", self.EXCHANGE)

        self._channel.exchange_declare(
            exchange=self.EXCHANGE,
            exchange_type=self.EXCHANGE_TYPE,
            durable=True,
            callback=self.on_exchange_declareok,
        )

    def on_exchange_declareok(self, _unused_frame: str) -> None:
        self.logger.info("Exchange declared")

        self.setup_queue()

    # ----------------------------------------
    def setup_queue(self) -> None:
        self.logger.info("Declaring queue '%s'", self.QUEUE)

        self._channel.queue_declare(
            queue=self.QUEUE,
            durable=True,
            callback=self.on_queue_declareok,
        )

    def on_queue_declareok(self, _unused_frame: str) -> None:
        self.logger.info(
            "Queue declared, binding to exchange. Routing key: '%s'", self.ROUTING_KEY
        )

        self._channel.queue_bind(
            exchange=self.EXCHANGE,
            queue=self.QUEUE,
            routing_key=self.ROUTING_KEY,
            callback=self.on_bindok,
        )

    def on_bindok(self, _unused_frame: str) -> None:
        self.logger.info("Queue bound")

        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok
        )

    def on_basic_qos_ok(self, _unused_frame: str) -> None:
        self.logger.info("QoS set")

        self.start_consuming()

    # ----------------------------------------
    def start_consuming(self) -> None:
        self.logger.info("Adding consumer cancellation callback")
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

        self.logger.info("Starting consumer")
        self._consumer_tag = self._channel.basic_consume(
            queue=self.QUEUE,
            on_message_callback=self.on_message,
        )
        self.was_consuming = True
        self._consuming = True

    def on_consumer_cancelled(self, _unused_frame: str) -> None:
        self.logger.info("Consumer was cancelled remotely")
        self._channel.close()

    def on_message(
        self,
        _unused_channel: Channel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: str | bytes,
    ) -> None:
        self.logger.debug(
            "Received message # %s from %s: %s",
            method.delivery_tag,
            properties.app_id,
            body,
        )
        try:
            self._handler.handle_message(body, properties.app_id)  # type: ignore
            self._channel.basic_ack(delivery_tag=method.delivery_tag)
        except AttributeError as e:
            self.logger.error("Handler not set: %s", e)
        except Exception as e:
            self.logger.error("Error handling message: %s", e)

    # ----------------------------------------
    def stop(self) -> None:
        if not self._closing:
            self._closing = True
            self.logger.info("Stopping")
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            self.logger.info("Stopped")

    def stop_consuming(self) -> None:
        if self._channel:
            self.logger.info("Sending a Basic.Cancel RPC command to RabbitMQ")
            self._channel.basic_cancel(
                self._consumer_tag,
                callback=self.on_cancelok,
            )

    def on_cancelok(self, _unused_frame: str) -> None:
        self.logger.info("RabbitMQ acknowledged the cancellation")
        self._consuming = False
        self._channel.close()

    # ----------------------------------------
    def run(self) -> None:
        self.connect()
        self._connection.ioloop.start()


def get_connection_manager() -> ConnectionManager:
    return ConnectionManager()
