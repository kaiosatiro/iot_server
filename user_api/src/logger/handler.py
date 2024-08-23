import logging
from logging import Formatter, LogRecord

from src.queue.channels import LogChannel


class LogHandler(logging.Handler):
    def __init__(
        self,
        channel: LogChannel,
        level: int = logging.NOTSET,
        formatter: Formatter | None = None,
        exchange: str = "logs",
        queue: str = "logs",
        routing_key: str | None = None,
        content_type: str = "text/plain",
        declare_exchange: bool = False,
    ):
        super().__init__(level=level)

        self.formatter = formatter
        self.exchange = exchange
        self.channel = channel
        self.queue = queue
        self.routing_key = routing_key if routing_key else "log.*"
        self.content_type = content_type
        self.exchange_declare = declare_exchange

        self.exg_declared = not declare_exchange
        self.channel_ready = False

        # Acquire a thread lock.
        self.createLock()

    def setup_channel(self) -> None:
        # Set logger if something went wrong connecting to the channel.
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)

        logger = logging.getLogger("setup_log_channel")
        logger.addHandler(handler)
        logger.propagate = False
        logger.setLevel(logging.WARNING)

        logger.info("Connecting Handler to Queue")
        self.channel.connect()

        logger.info("Configuring Handler Channel")
        if self.channel.status() and self.exchange_declare:
            self.channel.configure(
                exchange=self.exchange,
                queue=self.queue,
                routing_key=self.routing_key,
                declare_exchange=self.exchange_declare,
            )

        self.exg_declared = self.exchange_declare
        self.channel_ready = self.channel.status()

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
            # self.channel = None
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
