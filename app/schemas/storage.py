from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.schemas.task import Task

type TaskStore = dict[int, Task]


class StorageError(Exception):
    pass


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
