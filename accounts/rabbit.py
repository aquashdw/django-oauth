import json
import pika

from django.conf import settings

credentials = pika.PlainCredentials(settings.RABBIT_USER, settings.RABBIT_PASSWORD)
queue_name = settings.RABBIT_QUEUE_NAME


def send_mail(to, subject, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        settings.RABBIT_HOST,
        settings.RABBIT_PORT,
        credentials=credentials,
    ))

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    payload = json.dumps({'to': to, 'subject': subject, 'body': body})
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=payload,
    )
    connection.close()
