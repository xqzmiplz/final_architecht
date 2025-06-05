import pika
import json
import os
import time
from .models import Task
from . import db, create_app
from .rabbitmq import get_rabbitmq_connection

app = create_app()

# Константы группы и номера
GROUP = "BSBO-01-20"
NUMBER = "15"

def start_consumer():
    max_retries = 5
    app.logger.info("Starting RabbitMQ consumer")
    for attempt in range(max_retries):
        try:
            app.logger.info(f"Consumer attempt {attempt+1}/{max_retries}")
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            app.logger.info("Channel created")
            
            queue_name = f"queue.{GROUP}.{NUMBER}"
            
            # Объявление очереди
            channel.queue_declare(queue=queue_name, durable=True)
            app.logger.info(f"Queue declared: {queue_name}")
            
            # Объявление exchanges
            channel.exchange_declare(exchange=f"{GROUP}.{NUMBER}.fanout", exchange_type='fanout', durable=True)
            channel.exchange_declare(exchange=f"{GROUP}.{NUMBER}.direct", exchange_type='direct', durable=True)
            channel.exchange_declare(exchange=f"{GROUP}.{NUMBER}.topic", exchange_type='topic', durable=True)
            channel.exchange_declare(exchange=f"{GROUP}.{NUMBER}.headers", exchange_type='headers', durable=True)
            app.logger.info("Exchanges declared")
            
            # Привязка очереди к exchanges
            channel.queue_bind(
                exchange=f"{GROUP}.{NUMBER}.fanout",
                queue=queue_name
            )
            channel.queue_bind(
                exchange=f"{GROUP}.{NUMBER}.direct",
                queue=queue_name,
                routing_key=f"{GROUP}.{NUMBER}.routing.key"
            )
            channel.queue_bind(
                exchange=f"{GROUP}.{NUMBER}.topic",
                queue=queue_name,
                routing_key=f"{GROUP}.{NUMBER}.routing.key"
            )
            channel.queue_bind(
                exchange=f"{GROUP}.{NUMBER}.headers",
                queue=queue_name,
                arguments={'group': GROUP, 'number': NUMBER, 'x-match': 'all'}
            )
            app.logger.info("Queue bindings created")
            
            def callback(ch, method, properties, body):
                with app.app_context():
                    try:
                        app.logger.info(f"Raw message body: {body}")
                        decoded_body = body.decode('utf-8')
                        app.logger.info(f"Decoded body: {decoded_body}")
                        
                        try:
                            message = json.loads(decoded_body)
                            app.logger.info(f"Parsed JSON message: {message}")
                            
                            if message.get('event_type') == 'task_created':
                                task = Task.query.get(message['task_id'])
                                if task:
                                    with open('task_log.txt', 'a') as f:
                                        f.write(f"Task created: {task.description}\n")
                                    app.logger.info(f"Logged task: {task.description}")
                                else:
                                    app.logger.warning(f"Task with id {message['task_id']} not found")
                            else:
                                app.logger.info(f"Demo JSON message processed: {message.get('message')}")
                        except json.JSONDecodeError:
                            app.logger.info(f"Non-JSON demo message processed: {decoded_body}")
                            
                        # Ручное подтверждение сообщения
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        app.logger.info(f"Message acknowledged: {decoded_body}")
                        
                    except Exception as e:
                        app.logger.error(f"Error processing message: {str(e)}, Raw body: {body}")
                        # Не подтверждаем сообщение в случае ошибки, чтобы оно осталось в очереди
                        # Можно добавить ch.basic_nack() для возврата в очередь, если требуется
                
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            app.logger.info("Consumer started. Waiting for messages...")
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError as e:
            app.logger.error(f"AMQP connection error: {str(e)} (attempt {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                app.logger.warning(f"Retrying consumer in 10s...")
                time.sleep(10)
                continue
            raise
        except Exception as e:
            app.logger.error(f"Unexpected error in consumer: {str(e)}")
            raise
        finally:
            if 'connection' in locals():
                app.logger.info("Closing RabbitMQ connection")
                connection.close()

if __name__ == "__main__":
    with app.app_context():
        app.logger.info("Initializing consumer")
        start_consumer()