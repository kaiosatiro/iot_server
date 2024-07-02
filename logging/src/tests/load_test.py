#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='logs', durable=True)

msg = """
    {
        "timestamp": "2021-09-09T12:00:00",
        "device_id": "device_1",
        "temperature": 25.0,
        "humidity": 60.0
    }

"""
for i in range(100000):

    message = f"{msg}! {i}"
    channel.basic_publish(
        exchange='',
        routing_key='logs',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        ))

connection.close()