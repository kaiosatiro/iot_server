import atexit
import json
import logging.config
import logging.handlers
import pathlib

logger = logging.getLogger(__name__)

# Function to setup logging configuration from a JSON
def setup_logging():
    config_file = pathlib.Path("logger-config.json")
    with open(config_file) as f_init:
        config = json.load(f_init)
    
    logging.config.dictConfig(config)

    # get the queue handler
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)
    

def test():
    setup_logging()
    logging.basicConfig(level="INFO")
    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("exception message")


if __name__ == "__main__":
    test()