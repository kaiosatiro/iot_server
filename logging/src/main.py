# Description: Main entry point for the logging service
import logging.config
import logging.handlers
from os import _exit as os_exit
from sys import exit as sysexit

from src.consumer import Consumer
from src.core.time_service import get_time_service
from src.logger.setup import setup_logging

setup_logging()

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Starting the logging service")

    try:
        _ = get_time_service()
        consumer = Consumer()
        consumer.run()
    except KeyboardInterrupt:
        logger.warning("Shutting down the logging service")
        try:
            sysexit(0)
        except SystemExit:
            os_exit(0)
