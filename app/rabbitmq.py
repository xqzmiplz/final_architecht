import pika
import json
import os
import time
from functools import wraps
from flask import current_app

def get_rabbitmq_connection(retries=15, delay=10):
    current_app.logger.info("Starting RabbitMQ connection attempts")
    for attempt in range(retries):
        try:
            current_app.logger.info(f"Attempting RabbitMQ connection (attempt {attempt+1}/{retries})")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
                    port=5672,
                    credentials=pika.PlainCredentials(
                        os.getenv('RABBITMQ_USER', 'guest'),
                        os.getenv('RABBITMQ_PASSWORD', 'guest')
                    )
                )
            )
            current_app.logger.info("RabbitMQ connection established successfully")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            current_app.logger.warning(f"RabbitMQ connection failed: {str(e)} (attempt {attempt+1}/{retries}), retrying in {delay}s...")
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            current_app.logger.error(f"All {retries} RabbitMQ connection attempts failed")
            raise
        except Exception as e:
            current_app.logger.error(f"Unexpected error during RabbitMQ connection: {str(e)}")
            raise

def with_rabbitmq_channel(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        try:
            result = func(channel, *args, **kwargs)
            connection.close()
            return result
        except Exception as e:
            current_app.logger.error(f"RabbitMQ error: {str(e)}")
            connection.close()
            raise
    return wrapper