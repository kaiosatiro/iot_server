import logging
from collections.abc import Callable
from threading import Thread

from pika import (  # type: ignore
    BasicProperties,
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from pika.channel import Channel  # type: ignore

from src.config import settings


class PublishingManager(Thread):
    def __init__(self, testmode: bool = False, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.name = "PublisherManager"
        self.testmode = testmode
        self.is_running = True

        self.host = settings.RABBITMQ_DNS
        self._connection: BlockingConnection = None
        self.channels: dict[str, Channel] = {}

        # Set logger if something went wrong connecting to the channel.
        self.logger = logging.getLogger(self.__class__.__name__)
        self.log_handler = logging.StreamHandler()
        self.logger.addHandler(self.log_handler)
        self.logger.propagate = False
        self.logger.setLevel(logging.WARNING)

        try:
            if not self.testmode:
                self.logger.info("Connecting Logger to Queue")
                self.connect()
        except Exception as e:
            self.logger.error(f"Error connecting to Queue: {e}")
            self.stop()
        finally:
            self.logger.removeHandler(self.log_handler)
            del self.log_handler

    def open_channel(self, tag: str) -> Channel:
        channel = self._connection.channel()
        self.channels[tag] = channel
        return channel

    def connect(self) -> None:
        credentials = PlainCredentials("guest", "guest")
        parameters = ConnectionParameters(
            self.host, credentials=credentials, heartbeat=0
        )
        self._connection = BlockingConnection(parameters)

    def status(self) -> bool:
        try:
            if self._connection.is_open:
                return True
        except AttributeError as e:
            self.logger.error(f"Error checking status: {e}")
        return False

    def close_connection(self) -> None:
        for channel in self.channels.values():
            channel.close()
        self._connection.close()

    def run(self) -> None:
        while self.is_running:
            self._connection.process_data_events(time_limit=1)

    def stop(self) -> None:
        self.is_running = False
        # Wait until all the data events have been processed
        self._connection.process_data_events(time_limit=1)
        if self._connection.is_open:
            self.close_connection()

    def publish(
        self,
        call: Callable[[str, str, str | bytes, BasicProperties | None, bool], None],
    ) -> None:
        logging.getLogger(self.__class__.__name__).info("Publishing message")
        self._connection.add_callback_threadsafe(lambda: call)


def get_queue_access() -> PublishingManager:
    return PublishingManager()
