# Module to pull messages from a RabbitMQ server and handle them using the provided message handler.

import pika
from src.handler import Handler

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
        logger.debug(f"Received message: {body}")
        msg_handler.handle_message(body, properties)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    logger.debug("Connecting to RabbitMQ server")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='rabbitmq', port=5672,  # TODO: Change to environment variables?
            credentials=pika.PlainCredentials('guest', 'guest')  # TODO: Change to secure credentials?
        )
    )
    logger.debug("Connected to RabbitMQ server")
    channel = connection.channel()

    logger.debug("Declaring exchange and queue")
    channel.exchange_declare(exchange='logs', exchange_type='topic', durable=True)
    result = channel.queue_declare(queue='', durable=True)

    logger.debug("Binding queue to exchange")
    queue_name = result.method.queue
    channel.queue_bind(exchange='logs', queue=queue_name, routing_key='log.*')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    logger.info("Puller is waiting for messages")
    channel.start_consuming()
