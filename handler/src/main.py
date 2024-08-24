import logging.config
import logging.handlers

from src.consumer import Consumer
from src.logger.setup import setup_logging_config


setup_logging_config()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Starting the Handler service")

    consumer = Consumer()
    consumer.run()
