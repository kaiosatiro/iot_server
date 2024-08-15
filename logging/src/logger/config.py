from src.config import settings


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[ %(levelname)s | %(module)s | %(name)s | L%(lineno)d ] %(asctime)s : %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%"
        }
    },
    "handlers": {
    "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        },
    "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "level": settings.LOG_LEVEL,
        "formatter": "simple",
        "filename": settings.LOG_INFO_FILE,
        "maxBytes": 10000,
        "backupCount": 5
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["stderr", "file"],
            "respect_handler_level": "true",
        },
    },
    "loggers": {
        "root": {"level": settings.LOG_LEVEL, "handlers": ["queue_handler"]},
    },
}
