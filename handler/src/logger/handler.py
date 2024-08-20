import logging
from logging import Formatter, LogRecord

from src.logger.channel import LogChannel


class LogHandler(logging.Handler):
    def __init__(
        self,
        channel: LogChannel,
        level: int = logging.NOTSET,
        formatter: Formatter | None = None,
    ):
        super().__init__(level=level)

        self.formatter = formatter
        self.channel = channel

        self.channel_ready = False

        # Acquire a thread lock.
        self.createLock()

    def setup_channel(self) -> None:
        # Set logger if something went wrong connecting to the channel.
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(levelname)s] [%(name)s | L%(lineno)d] %(asctime)s : %(message)s",
        )
        handler.setFormatter(formatter)

        logger = logging.getLogger("setup_log_channel")
        logger.addHandler(handler)
        logger.propagate = False
        logger.setLevel(logging.INFO)

        logger.info("Connecting Handler to Queue")

        self.channel.connect()
        self.channel_ready = self.channel.status()
        self.channel.start()

        logger.info("Handler Channel Ready")

        # Remove logger to avoid shutdown message.
        logger.removeHandler(handler)

    def emit(self, record: LogRecord) -> None:
        self.acquire()
        try:
            if not self.channel_ready or not self.channel.status():
                self.setup_channel()

            formatted = self.format(record)
            self.channel.publish(message=formatted)

        except Exception:
            self.channel_ready = False
            self.channel.stop()
            self.handleError(record)
        finally:
            self.release()

    # def handle(self, record):
    #     rv = self.filter(record)
    #     if isinstance(rv, logging.LogRecord):
    #         record = rv
    #     if rv:
    #         self.acquire()
    #         try:
    #             self.emit(record)
    #         finally:
    #             self.release()
    #     return rv

    def __del__(self) -> None:
        self.close()
