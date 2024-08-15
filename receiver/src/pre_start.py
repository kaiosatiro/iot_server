import logging

from pika import (  # type: ignore
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.config import settings
from src.logger.setup import setup_logging_config


logger = logging.getLogger("PRE Start")

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


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


def main() -> None:
    logger.info("Initializing service | Testing QUEUE connection")
    connect()
    setup_logging_config()


if __name__ == "__main__":
    main()
    logger.info("Service finished initializing")
