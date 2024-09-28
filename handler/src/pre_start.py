# This script is used to test the connection to the RabbitMQ and the database,
#  before the application starts.
import logging

from pika import (  # type: ignore
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.database.engine import engine
from src.config import settings
from src.logger.setup import setup_logging_config


handler = logging.StreamHandler()
logger = logging.getLogger("Pre Start")
logger.addHandler(handler)
logger.propagate = False
logger.setLevel(logging.INFO)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


# Check if the connection to the RabbitMQ is working
@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def connect_queue() -> None:
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


# Check if the connection to the database is working
@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.WARN),
)
def check_db(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            session.scalar(select(1))
            Base = declarative_base()
            Base.metadata.reflect(engine)  # Waiting for db tables to be created
            assert Base.metadata.tables["message"] is not None
            assert Base.metadata.tables["device"] is not None
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service | Testing QUEUE connection")
    connect_queue()
    setup_logging_config()
    logger.info("Initializing service | Testing DB connection")
    check_db(engine)


if __name__ == "__main__":
    main()
    logger.info("Service finished initializing")
