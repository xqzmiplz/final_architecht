from flask import Blueprint, jsonify, request, current_app
from . import db, redis
from .models import Task
from .rabbitmq import with_rabbitmq_channel
from . import request_counter, task_gauge
import pika
import json
import os

bp = Blueprint('routes', __name__)

GROUP = "BSBO-01-20"
NUMBER = "15"

@bp.route('/tasks', methods=['GET'])
def get_tasks():
    # Увеличиваем счетчик запросов с метками
    request_counter.labels(method='GET', endpoint='/tasks').inc()
    
    # Обновляем gauge с количеством активных задач
    tasks_count = Task.query.count()
    task_gauge.set(tasks_count)
    
    # Попытка получить задачи из кэша
    cached_tasks = redis.get('tasks:all')
    if cached_tasks:
        current_app.logger.info("Returning tasks from cache")
        return jsonify(json.loads(cached_tasks))
    
    # Если кэш пуст, запрос к базе данных
    tasks = Task.query.all()
    tasks_data = [{'id': task.id, 'description': task.description} for task in tasks]
    
    # Сохранение в кэш
    redis.set('tasks:all', json.dumps(tasks_data))
    current_app.logger.info("Returning tasks from database and caching")
    return jsonify(tasks_data)

@bp.route('/tasks', methods=['POST'])
def create_task():
    # Увеличиваем счетчик запросов с метками
    request_counter.labels(method='POST', endpoint='/tasks').inc()
    
    data = request.get_json()
    description = data.get('description')
    if not description:
        return jsonify({'error': 'Description is required'}), 400
    
    task = Task(description=description)
    db.session.add(task)
    db.session.commit()
    
    # Очистка кэша
    redis.delete('tasks:all')
    
    # Обновляем gauge с количеством активных задач
    tasks_count = Task.query.count()
    task_gauge.set(tasks_count)
    
    # Публикация события создания задачи
    publish_task_created(task.id)
    
    current_app.logger.info(f"Created task: {task.description}")
    return jsonify({'id': task.id, 'description': task.description}), 201

@with_rabbitmq_channel
def publish_task_created(channel, task_id):
    message = {'event_type': 'task_created', 'task_id': task_id}
    body = json.dumps(message)
    current_app.logger.info(f"Sending task created message: {body}")
    channel.basic_publish(
        exchange=f"{GROUP}.{NUMBER}.direct",
        routing_key=f"{GROUP}.{NUMBER}.routing.key",
        body=body
    )

@bp.route('/send-demo-message/<msg_type>', methods=['GET'])
@with_rabbitmq_channel
def send_demo_message(channel, msg_type):
    # Увеличиваем счетчик запросов с метками
    request_counter.labels(method='GET', endpoint='/send-demo-message').inc()
    
    valid_types = ['fanout', 'direct', 'topic', 'headers']
    if msg_type not in valid_types:
        return jsonify({'error': 'Invalid message type'}), 400
    
    message = {'message': f"Test {msg_type} message"}
    exchange = f"{GROUP}.{NUMBER}.{msg_type}"
    
    # Установка routing_key и headers в зависимости от типа
    routing_key = f"{GROUP}.{NUMBER}.routing.key" if msg_type in ['direct', 'topic'] else ''
    arguments = {'group': GROUP, 'number': NUMBER} if msg_type == 'headers' else None
    
    body = json.dumps(message)
    current_app.logger.info(f"Sending demo message to exchange {exchange}: {body}")
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=body,
        properties=pika.BasicProperties(headers=arguments)
    )
    
    return jsonify({'status': f'{msg_type} message sent'})