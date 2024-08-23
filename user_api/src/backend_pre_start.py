import logging

from pika import (  # type: ignore
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.config import settings
from src.core.db import engine
from src.logger.setup import setup_logging_config

handler = logging.StreamHandler()
logger = logging.getLogger("Pre Start")
logger.addHandler(handler)
logger.propagate = False
logger.setLevel(logging.INFO)

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


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service | Testing QUEUE connection")
    connect()
    setup_logging_config()
    logger.info("Initializing service | Testing DB connection")
    init(engine)


if __name__ == "__main__":
    main()
    logger.info("Service finished initializing")
