from pydantic import BaseModel


class Task(BaseModel):
    id: int
    title: str
    description: str | None = None


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
