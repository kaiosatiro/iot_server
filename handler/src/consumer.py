import logging
from time import sleep

from src.core.abs import Handler
from src.core.connection import ConnectionManager
from src.core.message_handlers import get_handler


logger = logging.getLogger(__name__)


class Consumer:
    def __init__(self) -> None:
        self._handler: Handler = get_handler()
        self._connection: ConnectionManager = ConnectionManager(handler=self._handler)
        self._reconnect_delay = 0

    def run(self) -> None:
        while True:
            try:
                logger.info("Starting consumer")
                self._connection.run()
            except KeyboardInterrupt as e:
                logger.warning("KeyboardInterrupt in consumer: %s", e)
                self._handler.close()
                self._connection.stop()
                break
            except Exception as e:
                logger.error("Error in consumer: %s", e)
                self._connection.stop()
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._connection.should_reconnect:
            self._connection.stop()
            reconnect_delay = self._get_reconnect_delay()
            logger.info("Reconnecting after %d seconds", reconnect_delay)
            sleep(reconnect_delay)
            self._connection = ConnectionManager(handler=self._handler)

    def _get_reconnect_delay(self):
        if self._connection.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay
