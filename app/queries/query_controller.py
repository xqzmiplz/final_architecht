from flask import Blueprint, jsonify
from app.queries.query_handler import get_tasks

bp = Blueprint('queries', __name__, url_prefix='/queries')

@bp.route('/tasks', methods=['GET'])
def get_tasks_route():
    tasks = get_tasks()
    return jsonify([task.dict() for task in tasks])