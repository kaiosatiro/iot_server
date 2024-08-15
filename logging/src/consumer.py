import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.connection import get_connection_manager, ConnectionManager
from src.core.handlers import get_handlers_manager
from src.core.abs import HandlerABC


logger = logging.getLogger(__name__)


class Consumer(object):
    def __init__(self):
        self._handler: HandlerABC = get_handlers_manager()
        self._connection: ConnectionManager = ConnectionManager(handler=self._handler)

    def run(self):
        while True:
            try:
                logger.info('Starting consumer')
                self._connection.run()
            except KeyboardInterrupt as e:
                logger.warning('KeyboardInterrupt in consumer: %s', e)
                self._connection.stop()
                break
            except Exception as e:
                logger.error('Error in consumer: %s', e)
                self._connection.stop()
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._connection.should_reconnect:
            logger.info('Reconnecting to RabbitMQ')
            self._connection.stop()

            max_tries = 60 * 5  # 5 minutes
            wait_seconds = 5

            @retry(
                stop=stop_after_attempt(max_tries),
                wait=wait_fixed(wait_seconds),
                before=before_log(logger, logging.INFO),
                after=after_log(logger, logging.WARN),
            )
            def reconnect_wrapper():
                self._connection.run()
            logger.info('Reconnecting to RabbitMQ in %d seconds...', wait_seconds)
            reconnect_wrapper()
