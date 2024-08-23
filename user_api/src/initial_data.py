import logging

from sqlmodel import Session

from src.core.db import engine, init_db
from src.logger.setup import setup_logging_config

setup_logging_config()
logger = logging.getLogger("Initial Data")


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
