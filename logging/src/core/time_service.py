import logging
import threading
import time
from datetime import datetime

from src.config import settings
from src.core.abs import SingletonTimeService


logger = logging.getLogger(__name__)


class TimeService(metaclass=SingletonTimeService):
    def __init__(self) -> None:
        self.current_time = datetime.now()
        self.current_date = self.current_time.strftime("%Y-%m-%d")
        self.update_interval = settings.TIME_SERVICE_UPDATE_INTERVAL
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._update_time)
        self._thread.daemon = True

        logger.info("Starting TimeService")
        self._thread.start()

    def _update_time(self) -> None:
        while not self._stop_event.is_set():
            self.current_time = datetime.now()
            self.current_date = self.current_time.strftime("%Y-%m-%d")
            time.sleep(self.update_interval)

    def get_current_time(self) -> datetime:
        return self.current_time

    def get_current_date(self) -> str:
        return self.current_date

    def stop(self):
        self._stop_event.set()
        self._thread.join()


def get_time_service() -> TimeService:
    return TimeService()
