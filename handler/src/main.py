import logging

from src.logger.setup import setup_logging_config

setup_logging_config()
logger = logging.getLogger(__name__)

try:
    from random import randint
    from time import sleep

    while True:
        logger.info(f"Info message {randint(1, 10000)}")
        sleep(1)
except KeyboardInterrupt:
    exit(0)
