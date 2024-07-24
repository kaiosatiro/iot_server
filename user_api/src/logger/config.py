LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": 'false',
    "formatters": {
        "simple": {
            "format": "USER-API [%(levelname)s |%(module)s| L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
    "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        },
    "queue": {
        "class": "python_logging_rabbitmq.RabbitMQHandler",
        "level": "INFO",
        'host': 'rabbitmq',
        'port': "5672",
        "formatter": "simple",
        "exchange":'logs',
        "routing_key_formatter":lambda key: 'log.userapi',
        "declare_exchange":True,
        # "record_fields":['app', 'levelname', 'module', 'asctime', 'msg'],
        # "fields":{'app': 'USERAPI'},
        },
    "queue_handler":{
        "class": "logging.handlers.QueueHandler",
        "handlers": [
            "stderr",
            "queue"
            ],
        "respect_handler_level": 'true'
        }
    },
    "loggers": {
        "root": {
            "level": "INFO",
            "handlers": [
                "queue_handler"
            ]
        }
    }
}