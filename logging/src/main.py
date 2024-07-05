# Description: Main entry point for the logging service

from sys import exit as sysexit
from os import _exit as os_exit

from atexit import register as atexitregister
from json import load as json_load
import logging.config
import logging.handlers
from pathlib import Path

from src.puller import puller
from src.handler import get_handler
from src.data import get_db_manager

logger = logging.getLogger(__name__)


# Function to setup logging configuration from a JSON
def setup_logging():
    config_file = Path("logger-config.json")
    with open(config_file) as f_init:
        config = json_load(f_init)

    # TODO: Add the basic config in case the JSON file does not have it

    logging.config.dictConfig(config)

    # get the queue handler
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexitregister(queue_handler.listener.stop)


if __name__ == '__main__':
    setup_logging()
    logging.basicConfig()
    logger.info("Starting the logging service")

    db = get_db_manager()
    handler_mng = get_handler(db)
    try:
        logger.debug("Initializing puller")
        puller(handler_mng)

    except KeyboardInterrupt:
        logger.info("Shutting down the logging service")
        try:
            sysexit(0)
        except SystemExit:
            os_exit(0)
