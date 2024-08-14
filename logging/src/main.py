# Description: Main entry point for the logging service
from sys import exit as sysexit
from os import _exit as os_exit

import logging.config
import logging.handlers

from src.handler import get_handler
from src.data import get_db_manager
from src.logger.setup import setup_logging
from src.config import settings


if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger(__name__)
    # logging.basicConfig()
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
