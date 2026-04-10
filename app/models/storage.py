from abc import ABC, abstractmethod

from app.models.task import Task
from pydantic import BaseModel

type TaskMap = dict[int, Task]


class StorageError(Exception):
    pass


class JSONSaveData(BaseModel):
    next_id: int
    tasks: TaskMap


class StorageAdapter(ABC):
    @abstractmethod
    def save(self, data: JSONSaveData) -> None:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def load(self) -> JSONSaveData:
        raise NotImplementedError()  # pragma: no cover
