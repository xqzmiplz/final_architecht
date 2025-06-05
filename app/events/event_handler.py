from app import db
from app.read_model.task_read_model import TaskReadModel
from app.events.models import Event

def handle_event(event: Event):
    if event.event_type == 'TaskCreated':
        task_data = event.event_data
        task = TaskReadModel(id=task_data['id'], description=task_data['description'], version=1)
        db.session.add(task)
    elif event.event_type == 'TaskUpdated':
        task_data = event.event_data
        task = TaskReadModel.query.get(task_data['id'])
        if task:
            task.description = task_data['description']
            task.version += 1
    db.session.commit()