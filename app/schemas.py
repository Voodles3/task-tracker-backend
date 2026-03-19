from pydantic import BaseModel
from abc import ABC, abstractmethod


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


type TaskStore = dict[int, Task]


class JSONSaveData(BaseModel):
    next_id: int
    tasks: TaskStore


class StorageAdapter(ABC):
    @abstractmethod
    def save(self, data: JSONSaveData) -> None:
        raise NotImplementedError()

    @abstractmethod
    def load(self) -> JSONSaveData:
        raise NotImplementedError()
