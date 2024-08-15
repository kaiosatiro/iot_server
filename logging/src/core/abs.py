from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from threading import Lock


class SingletonConnection(type):
    _instances = {}  # type: ignore
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonTimeService(type):
    _instances = {}  # type: ignore
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonMetaHandler(ABCMeta):
    _instances = {}  # type: ignore
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class HandlerABC(ABC):
    @abstractmethod
    def handle_message(self, msg: str, *args, **kwargs) -> None: ...  # type: ignore


class DB(ABC):
    @abstractmethod
    def save(self, data: str, *args, **kwargs) -> None: ...  # type: ignore

    @abstractmethod
    def set_origin(self, origin: str) -> None: ...


class DataManager(ABC):
    @abstractmethod
    def get_local(self) -> DB: ...

    @abstractmethod
    def get_remote(self) -> DB: ...
