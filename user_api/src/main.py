from logging import getLogger

from logger.setup import setup_logging


if __name__ == '__main__':
    setup_logging()
    logger = getLogger(__name__)
    # logging.basicConfig()
    logger.info("Starting the User API service")

# postgresurl= "postgresql://postgres:postgres@localhost:5432/app"
