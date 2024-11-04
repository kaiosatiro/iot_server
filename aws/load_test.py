#!/usr/bin/env python3
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials('guest', 'guest'),
    )
)
channel = connection.channel()

channel.queue_declare(queue='logs', durable=True)

msg = """
    {
        "timestamp": "2021-09-09T12:00:00",
        "device_id": "9g786s0agd6",
        "temperature": 25.0,
        "humidity": 60.0
    }

"""
for i in range(12):

    message = f"{msg}! {i}"
    channel.basic_publish(
        exchange='',
        routing_key='logs',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        ))

connection.close()