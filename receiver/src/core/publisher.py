import logging
from abc import ABCMeta, abstractmethod

import pika
from pika.channel import Channel
from threading import Thread, Lock

import pika.channel

from src.config import settings


class SingletonMeta(ABCMeta):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ABSQueueChannel(object):
    __metaclass__ = SingletonMeta

    @abstractmethod
    def open_channel(self, tag:str) -> Channel:
        pass
    
    @abstractmethod
    def get_connection_status(self) -> bool:
        pass

    @abstractmethod
    def close_connection(self):
        pass
        
    # @abstractmethod
    # def on_channel_open(self, channel):

    # @abstractmethod
    # def on_channel_closed(self, channel, reason):
    #     #logger
    #     self._channel = None
    #     if not self._stopping:
    #         self._connection.close()


class PublishingManager(metaclass=SingletonMeta):
    def __init__(self):
        self.host = settings.RABBITMQ_DNS
        self._connection = None
        self.channels = {}

        self.connect()
    
    def open_channel(self, tag:str) -> Channel:
        channel = self._connection.channel()
        self.channels[tag] = channel
        return channel

    def get_connection_status(self) -> bool:
        return self._connection.is_open
    
    #------------------------------------------------------------------------------
    def on_connection_open(self, connection):
        pass
    
    def on_connection_open_error(self, unused_connection, err):
        # logger.error('Connection open failed, reopening in 5 seconds: %s', err)
        self._connection.ioloop.call_later(5, self._connection.ioloop.stop)
        
    def on_connection_closed(self, unused_connection, reason):
        self._connection.ioloop.stop()
    
    def connect(self):
        parameters = pika.ConnectionParameters(host=self.host)
        self._connection = pika.SelectConnection(
            parameters,
            on_open_callback=self.on_connection_open,
            on_close_callback=self.on_connection_closed,
            on_open_error_callback=self.on_connection_open_error
            )

        self.io_loop_thread = Thread(target=self._connection.ioloop.start)
        self.io_loop_thread.daemon = True
        self.io_loop_thread.start()
    #------------------------------------------------------------------------------

    def close_connection(self):
        for channel in self.channels.values():
            channel.close()
        self._connection.close()
        self.io_loop_thread.join()


def get_queue_access() -> ABSQueueChannel:
    return PublishingManager()
