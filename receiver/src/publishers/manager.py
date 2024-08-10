import logging

from pika import ConnectionParameters, BlockingConnection, PlainCredentials
from pika.channel import Channel
from threading import Thread

from src.config import settings
from src.publishers.abs import ABSQueueConnectionManager


logger = logging.getHandlerByName("stderr")


class PublishingManager(ABSQueueConnectionManager, Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.name = "PublisherManager"
        self.is_running = True
        
        self.host = settings.RABBITMQ_DNS
        self._connection = None
        self.channels = {}


        # Set logger if something went wrong connecting to the channel.
        self.logger = logging.getLogger(__class__.__name__)
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
    
    def open_channel(self, tag:str) -> Channel:
        channel = self._connection.channel()
        self.channels[tag] = channel
        return channel
      
    def connect(self):
        credentials = PlainCredentials("guest", "guest")
        parameters = ConnectionParameters(
            self.host,
            credentials=credentials,
            heartbeat=3600
            )
        self._connection = BlockingConnection(parameters)
    
    def status(self) -> bool:
        return self._connection.is_open

    def close_connection(self):
        for channel in self.channels.values():
            channel.close()
        self._connection.close()
    
    def run(self):
        while self.is_running:
            self._connection.process_data_events(time_limit=1)

    def stop(self):
        self.is_running = False
        # Wait until all the data events have been processed
        self._connection.process_data_events(time_limit=1)
        if self._connection.is_open:
            self.close_connection()

    def publish(self, call):
        self._connection.add_callback_threadsafe(lambda: call)


def get_queue_access() -> PublishingManager:
    return PublishingManager()
