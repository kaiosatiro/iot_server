import logging

from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

from src.config import settings

logger = logging.getLogger("PRE Start")

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def connect() -> None:
    try:
        logger.info("Connecting to RabbitMQ")

        connection = BlockingConnection(
            ConnectionParameters(
                host=settings.RABBITMQ_DNS, port=settings.RABBITMQ_PORT,
                credentials=PlainCredentials('guest', 'guest')
            )
        )
        channel = connection.channel()

        channel.exchange_declare(exchange='logs', exchange_type='topic', duable=True)
        queue = channel.queue_declare(queue='logs', durable=True)
        channel.queue_bind(exchange='logs', queue=queue.method.queue, routing_key='log.*')

        logger.info("Connected to RabbitMQ")

        channel.basic_publish(
            exchange='logs', routing_key='log.info', body='PRE started!'
        )
        connection.close()
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service | Testing QUEUE connection")
    connect()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
