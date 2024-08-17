from src.config import settings
from src.logger.channel import LogChannel


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    # "filters": {
    #     "correlation_id": {
    #         "()": "asgi_correlation_id.CorrelationIdFilter",
    #         "uuid_length": 8 if settings.ENVIRONMENT == "dev" else 32,
    #         "default_value": "-",
    #     },
    # },
    "formatters": {
        "simple": {
            "format": f"{settings.HANDLER_ID} [%(levelname)s] [%(name)s | L%(lineno)d] %(asctime)s : %(message)s",
            "datefmt": "%H:%M:%S",
        }
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "queue": {
            "class": "src.logger.handler.LogHandler",
            "channel": LogChannel(),
            "level": settings.LOG_LEVEL,
            "formatter": "simple",
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["stderr", "queue"],
            "respect_handler_level": "true",
            # "filters": ["correlation_id"],
        },
    },
    "loggers": {
        "root": {"level": settings.LOG_LEVEL, "handlers": ["queue_handler"]},
    },
}
