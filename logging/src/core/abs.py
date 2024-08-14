from abc import ABCMeta
from threading import Lock


class SingletonMetaConnection(ABCMeta):
    _instances = {}  # type: ignore
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):  # type: ignore
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
