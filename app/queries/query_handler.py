from app.read_model.task_read_model import TaskReadModel
from app.queries.dtos import TaskDto

def get_tasks():
    tasks = TaskReadModel.query.all()
    return [TaskDto(id=task.id, description=task.description) for task in tasks]