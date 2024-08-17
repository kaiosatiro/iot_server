import logging
from threading import Thread

from pika.channel import Channel  # type: ignore
from pika import (  # type: ignore
    BasicProperties,
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)

from src.config import settings
from src.logger.abs import SingletonMetaConnection


logger = logging.getLogger(__name__)


class LogChannel(Thread, metaclass=SingletonMetaConnection):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.daemon = True

        self._name = "PublisherManager"

        self.is_running = True

        self._host = settings.RABBITMQ_DNS
        self._port = settings.RABBITMQ_PORT
        self._username = settings.RABBITMQ_USER
        self._password = settings.RABBITMQ_PASSWORD

        self._connection: BlockingConnection = None
        self._channel: Channel = None
        self._exchange = settings.LOG_EXCHANGE
        self._queue = settings.LOG_QUEUE
        self._routing_key = settings.LOG_ROUTING_KEY

        self._message_properties = BasicProperties(
            app_id=settings.HANDLER_ID,
            content_type="text/bytes",
            delivery_mode=2,
        )

        # Set logger if something went wrong connecting to the channel.
        self.logger = logging.getLogger(self.__class__.__name__)
        self.log_handler = logging.StreamHandler()
        self.logger.addHandler(self.log_handler)
        self.logger.propagate = False
        self.logger.setLevel(logging.WARNING)

        try:
            self.logger.info("Connecting Logger to Queue")
            self.connect()
        except Exception as e:
            self.logger.error(f"Error connecting to Queue: {e}")
            self.stop()
        finally:
            self.logger.removeHandler(self.log_handler)
            del self.log_handler

    # --------------------------------- #
    def connect(self) -> None:
        self.logger.info("Connecting to Queue")

        credentials = PlainCredentials(self._username, self._password)
        parameters = ConnectionParameters(
            self._host, self._port, credentials=credentials, heartbeat=3600
        )
        self._connection = BlockingConnection(parameters)

        self.logger.info("Opening Channel")
        self._channel = self._connection.channel()

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
        )

        self.logger.info(
            f"Binding {self._queue} to {self._exchange} with {self._routing_key}"
        )
        self._channel.queue_bind(
            exchange=self._exchange,
            queue=self._queue,
            routing_key=self._routing_key,
        )

    # --------------------------------- #
    def status(self) -> bool:
        try:
            if self._connection.is_open:
                return True
        except AttributeError as e:
            logger.error(f"Error checking status: {e}")
        return False

    def _close_connection(self) -> None:
        self._connection.close()

    def run(self) -> None:
        while self.is_running:
            self._connection.process_data_events(time_limit=1)

    def stop(self) -> None:
        self.is_running = False
        # Wait until all the data events have been processed
        self._connection.process_data_events(time_limit=1)
        if self._connection.is_open:
            self._close_connection()

    # --------------------------------- #
    def _publish(self, message: str) -> None:
        self._channel.basic_publish(
            exchange=self._exchange,
            routing_key=self._routing_key,
            body=message,  # TODO: .encode()?
            properties=self._message_properties,
            mandatory=True,
        )

    def publish(self, message: str) -> None:
        self._connection.add_callback_threadsafe(lambda: self._publish(message))


def get_channel() -> LogChannel:
    return LogChannel()
