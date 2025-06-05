from flask import Blueprint, request, jsonify
from app.commands.dtos import CreateTaskDto, UpdateTaskDto
from app.commands.command_handler import handle_create_task, handle_update_task
from app import request_counter, task_gauge  # Импортируем метрики

bp = Blueprint('commands', __name__, url_prefix='/commands')

@bp.route('/create-task', methods=['POST'])
def create_task():
    # Увеличиваем счетчик запросов с метками
    request_counter.labels(method='POST', endpoint='/commands/create-task').inc()
    
    data = request.get_json()
    dto = CreateTaskDto(**data)
    task_id = handle_create_task(dto)
    
    # Обновляем gauge с количеством активных задач
    from app.read_model.task_read_model import TaskReadModel
    tasks_count = TaskReadModel.query.count()
    task_gauge.set(tasks_count)
    
    return jsonify({'task_id': task_id}), 201

@bp.route('/update-task', methods=['POST'])
def update_task():
    # Увеличиваем счетчик запросов с метками
    request_counter.labels(method='POST', endpoint='/commands/update-task').inc()
    
    data = request.get_json()
    dto = UpdateTaskDto(**data)
    handle_update_task(dto)
    
    # Обновляем gauge с количеством активных задач
    from app.read_model.task_read_model import TaskReadModel
    tasks_count = TaskReadModel.query.count()
    task_gauge.set(tasks_count)
    
    return jsonify({'status': 'Task updated'}), 200