import logging.config

from atexit import register as atexitregister

from src.logger.config import LOG_CONFIG


def setup_logging():
    logging.config.dictConfig(LOG_CONFIG)
    # get the queue handler
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexitregister(queue_handler.listener.stop)
