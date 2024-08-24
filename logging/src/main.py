import logging.config
import logging.handlers

from src.consumer import Consumer
from src.core.time_service import get_time_service
from src.logger.setup import setup_logging


setup_logging()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Starting the logging service")

    _ = get_time_service()  # Starting the time service
    consumer = Consumer()
    consumer.run()
