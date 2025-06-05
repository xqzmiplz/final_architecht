import uuid
from app import db
from app.events.models import Event
from app.commands.dtos import CreateTaskDto, UpdateTaskDto
from app.events.event_handler import handle_event

def handle_create_task(command: CreateTaskDto):
    task_id = str(uuid.uuid4())
    event_data = {'id': task_id, 'description': command.description}
    event = Event(aggregate_id=task_id, event_type='TaskCreated', event_data=event_data)
    db.session.add(event)
    db.session.commit()
    handle_event(event)
    return task_id

def handle_update_task(command: UpdateTaskDto):
    event_data = {'id': command.task_id, 'description': command.description}
    event = Event(aggregate_id=command.task_id, event_type='TaskUpdated', event_data=event_data)
    db.session.add(event)
    db.session.commit()
    handle_event(event)