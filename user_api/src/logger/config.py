from src.core.config import settings

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            "uuid_length": 8 if settings.ENVIRONMENT == "dev" else 32,
            "default_value": "-",
        },
    },
    "formatters": {
        "simple": {
            "format": f"{settings.USERAPI_ID} [%(levelname)s] [%(name)s | L%(lineno)d] %(asctime)s [%(correlation_id)s]: %(message)s",
            "datefmt": "%H:%M:%S",
        }
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING" if settings.ENVIRONMENT == "production" else "DEBUG",
            # "filters": ["correlation_id"],
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "queue": {
            "class": "python_logging_rabbitmq.RabbitMQHandler",
            "level": settings.LOG_LEVEL,
            "host": settings.RABBITMQ_DNS,
            "port": settings.RABBITMQ_PORT,
            # "filters": ["correlation_id"],
            "formatter": "simple",
            "exchange": settings.LOG_EXCHANGE,
            "routing_key_formatter": lambda key: settings.LOG_ROUTING_KEY,
            "declare_exchange": True,
            # "record_fields":['app', 'levelname', 'module', 'asctime', 'msg'],
            # "fields":{'app': 'USERAPI'},
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["stderr", "queue"],
            "respect_handler_level": "true",
            "filters": ["correlation_id"],
        },
    },
    "loggers": {
        "root": {"level": settings.LOG_LEVEL, "handlers": ["queue_handler"]},
    },
}
