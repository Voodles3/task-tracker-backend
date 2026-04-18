from abc import ABC, abstractmethod
from logging import getLogger
from threading import Lock

from app.models.list import TaskList
from app.models.task import Task
from pydantic import BaseModel

logger = getLogger(__name__)

type TaskMap = dict[int, Task]
type TaskListMap = dict[int, TaskList]


class StorageError(Exception):
    pass


class JSONSaveData(BaseModel):
    schema_version: int = 2
    next_task_id: int
    next_list_id: int
    tasks: TaskMap
    lists: TaskListMap


class StorageAdapter(ABC):
    @abstractmethod
    def save(self, data: JSONSaveData) -> None:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def load(self) -> JSONSaveData:
        raise NotImplementedError()  # pragma: no cover
