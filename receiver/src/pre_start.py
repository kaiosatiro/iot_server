import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.logger.setup import setup_logging

setup_logging()
logger = logging.getLogger("Pre Start")

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def connect(queue) -> None:
    try:
        ...
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service | Testing QUEUE connection")
    connect(...)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
