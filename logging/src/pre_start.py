# This script is used to check if the log folder exists and if
#   the connection to the RabbitMQ server is working, before initializing the main service.
# The Log folder is where this service store the logs from the
#   system locally, and it should/is binded to a folder outside the container.
import logging
import os

from pika import (  # type: ignore
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.config import settings
from src.logger.setup import setup_logging

logger = logging.getLogger("Pre Start")


max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


# Check if the connection to the RabbitMQ server is working for several times
@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def connect() -> None:
    try:
        logger.info("Connecting to RabbitMQ")

        connection = BlockingConnection(
            ConnectionParameters(
                host=settings.RABBITMQ_DNS,
                port=settings.RABBITMQ_PORT,
                credentials=PlainCredentials("guest", "guest"),
            )
        )
        assert connection.is_open
        connection.close()

    except Exception as e:
        logger.error(e)
        raise e


# Check if the log folder exists
def check_log_folder() -> bool:
    return os.path.exists(settings.LOG_INFO_LOCAL_PATH)


def main() -> None:
    logger.info("Initializing service | Checking log folder")
    if check_log_folder():
        setup_logging()
        logger.info("Initializing service | Testing QUEUE connection")
        connect()
        logger.info("Service finished initializing")
    else:
        logger.error("Log folder does not exist")
        raise Exception("Log folder does not exist")


if __name__ == "__main__":
    main()
