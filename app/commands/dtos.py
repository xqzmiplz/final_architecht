from pydantic import BaseModel

class CreateTaskDto(BaseModel):
    description: str

class UpdateTaskDto(BaseModel):
    task_id: str
    description: str