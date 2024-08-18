from abc import ABC, abstractmethod
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


class Handler(ABC):
    @abstractmethod
    def handle_message(self, body: str | bytes, *args, **kwargs) -> None: ...  # type: ignore

    @abstractmethod
    def close(self) -> None: ...  # type: ignore
