import pika
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def callback(ch, method, properties, body):
    print(f"Received message: {body}")

# Get RabbitMQ host and port from environment variables
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))

# Create connection parameters using RabbitMQ service name and port
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port))
channel = connection.channel()

channel.queue_declare(queue='flask_messages')

channel.basic_consume(queue='flask_messages',
                      on_message_callback=callback,
                      auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
