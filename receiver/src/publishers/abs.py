from abc import ABC, ABCMeta, abstractmethod
from threading import Lock

from pika.channel import Channel  # type: ignore


class SingletonMetaConnection(ABCMeta):
    _instances = {}  # type: ignore
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonMetaChannel(ABCMeta):
    _instances = {}  # type: ignore
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonMetaChannelB(ABCMeta):
    _instances = {}  # type: ignore
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class ABSQueueConnectionManager(ABC, metaclass=SingletonMetaConnection):
    @abstractmethod
    def open_channel(self, tag: str) -> Channel: ...

    @abstractmethod
    def status(self) -> bool: ...

    @abstractmethod
    def close_connection(self) -> None: ...

    @abstractmethod
    def publish(self, call) -> None: ...  # type: ignore


class ABSQueueChannel(ABC, Channel, metaclass=SingletonMetaChannel):  # type: ignore
    @abstractmethod
    def connect(self) -> None: ...

    @abstractmethod
    def setup(self) -> None: ...

    @abstractmethod
    def publish_message(self, message, *args, **kwargs) -> None: ...  # type: ignore

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def status(self) -> bool: ...

    @abstractmethod
    def configure(
        self, exchange: str, queue: str, routing_key: str, declare_exchange: bool
    ) -> None: ...
