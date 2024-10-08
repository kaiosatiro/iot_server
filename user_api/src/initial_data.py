import logging

from sqlmodel import Session

from src.core.config import settings
from src.core.db import engine, init_db
from src.example_data import insert_example_data
from src.logger.setup import setup_logging_config

setup_logging_config()
logger = logging.getLogger("Initial Data")


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def insert_data() -> None:
    with Session(engine) as session:
        insert_example_data(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")

    if settings.INSERT_EXAMPLE_DATA:
        logger.info("Inserting example data")
        insert_data()
        logger.info("Example data inserted")


if __name__ == "__main__":
    main()
