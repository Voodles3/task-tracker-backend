from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.models.task import Task

type TaskMap = dict[int, Task]


class StorageError(Exception):
    pass


class JSONSaveData(BaseModel):
    next_id: int
    tasks: TaskMap


class StorageAdapter(ABC):
    @abstractmethod
    def save(self, data: JSONSaveData) -> None:
        raise NotImplementedError()

    @abstractmethod
    def load(self) -> JSONSaveData:
        raise NotImplementedError()
