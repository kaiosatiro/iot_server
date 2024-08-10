from abc import ABC, ABCMeta, abstractmethod
from threading import Lock

from pika.channel import Channel
from pika.connection import Connection


class SingletonMetaConnection(ABCMeta):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonMetaChannel(ABCMeta):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ABSQueueConnectionManager(ABC, metaclass=SingletonMetaConnection):
    @abstractmethod
    def open_channel(self, tag:str, callback) -> Channel: ...
    
    @abstractmethod
    def status(self) -> bool: ...
        
    @abstractmethod
    def close_connection(self) -> None: ...

    @abstractmethod
    def publish(self, call) -> None: ...


class ABSQueueChannel(ABC, Channel, metaclass=SingletonMetaChannel):   
    @abstractmethod
    def connect(self): ...

    @abstractmethod
    def setup(self): ...

    @abstractmethod
    def publish_message(self, message): ...

    @abstractmethod
    def stop(self): ...

    @abstractmethod
    def status(self): ...

    @abstractmethod
    def configure(self, exchange: str, queue: str, routing_key: str, declare_exchange: bool): ...
