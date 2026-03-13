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


class JSONSaveData(BaseModel):
    next_id: int
    tasks: list[Task]


class StorageAdapter(ABC):
    @abstractmethod
    def save(self, tasks: list[Task], next_id: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    def load(self) -> tuple[list[Task], int]:
        raise NotImplementedError()
