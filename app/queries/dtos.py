from pydantic import BaseModel

class TaskDto(BaseModel):
    id: str
    description: str