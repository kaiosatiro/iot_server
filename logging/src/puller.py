# Module to pull messages from a RabbitMQ server and handle them using the provided message handler.

import pika
from handler import Handler

from logging import getLogger

logger = getLogger(__name__)


def puller(msg_handler: Handler):
    """
    Function to pull messages from a RabbitMQ server and handle them using the provided message handler.

    Args:
        msg_handler (Handler): The message handler object that will handle the received messages.

    Returns:
        None
    """
    # Callback function to handle messages
    def callback(ch, method, properties, body) -> None:
        msg_handler.handle_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    logger.debug("Connecting to RabbitMQ server")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq', port=5672
        )
    )

    channel = connection.channel()
    channel.queue_declare(
        queue='logs', durable=True
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='logs', on_message_callback=callback
    )

    logger.info("Puller is waiting for messages")
    channel.start_consuming()
