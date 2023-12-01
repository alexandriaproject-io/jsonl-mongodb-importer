import pika
import ssl
import config
import json

# Set up SSL context
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True

parameters = pika.ConnectionParameters(
    host=config.RABBIT_HOST,
    port=config.RABBIT_PORT,
    virtual_host='/',
    credentials=pika.PlainCredentials(config.RABBIT_USERNAME, config.RABBIT_PASSWORD),
    ssl_options=pika.SSLOptions(context),
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue=config.RABBIT_QUEUE_NAME, durable=True)


def queue_job(job_id, job_data):
    # Set the message properties, including the unique message_id
    properties = pika.BasicProperties(
        message_id=job_id,  # Use job_id as unique message_id
        content_type='application/json',  # Indicate that the content is JSON
        delivery_mode=2,  # Make message persistent
    )

    # Publish the message with the unique message ID
    channel.basic_publish(
        exchange=config.RABBIT_QUEUE_EXCHANGE,
        routing_key=config.RABBIT_QUEUE_NAME,
        body=json.dumps(job_data),
        properties=properties
    )


def close_queue():
    connection.close()
