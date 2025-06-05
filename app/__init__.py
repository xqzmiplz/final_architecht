import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from prometheus_client import make_wsgi_app, Counter, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

db = SQLAlchemy()
redis = Redis(host=os.getenv('KEYDB_HOST', 'keydb'), port=6379, decode_responses=True)

# Кастомные метрики
request_counter = Counter(
    'todo_app_requests_total',
    'Total number of requests to the todo app',
    ['method', 'endpoint']
)
task_gauge = Gauge(
    'todo_app_active_tasks',
    'Number of active tasks in the todo app'
)

def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    # Конфигурация базы данных
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}"
        f"@{os.getenv('DB_HOST', 'db')}:5432/{os.getenv('DB_NAME', 'todo_db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализация расширений
    db.init_app(app)
    
    # Регистрация маршрутов
    with app.app_context():
        from app.commands.command_controller import bp as command_bp
        from app.queries.query_controller import bp as query_bp
        app.register_blueprint(command_bp)
        app.register_blueprint(query_bp)
        
        # Создание таблиц
        db.create_all()
    
    # Добавляем эндпоинт для Prometheus метрик
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })

    return app