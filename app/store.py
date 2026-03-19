from app.schemas import (
    Task,
    TaskCreate,
    TaskUpdate,
    StorageAdapter,
    TaskStore,
    JSONSaveData,
)
from logging import getLogger

logger = getLogger()


class Store:
    # SINGLETON PATTERN
    # So we can only have one Store
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Store":
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, storage: StorageAdapter) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self._tasks: TaskStore = {}
        self._next_id: int = 1

        self._storage = storage
        try:
            data = storage.load()
            self._tasks = data.tasks
            self._next_id = data.next_id
        except FileNotFoundError:
            logger.info("No save data to load, starting fresh!")

    def _get_next_id_and_increment(self) -> int:
        id = self._next_id
        self._next_id += 1
        return id

    def create_task(self, task_create: TaskCreate) -> Task:
        cached_tasks = self._tasks.copy()
        cached_next_id = self._next_id

        id = self._get_next_id_and_increment()
        task = Task(**task_create.model_dump(), id=id)
        self._tasks[id] = task
        try:
            self._storage.save(JSONSaveData(next_id=self._next_id, tasks=self._tasks))
            return task
        except Exception as e:
            self._tasks = cached_tasks
            self._next_id = cached_next_id
            raise Exception(f"Error creating new task: {e}")

    def get_task_by_id(self, task_id: int) -> Task | None:
        try:
            data = self._storage.load()
            return data.tasks.get(task_id)
        except FileNotFoundError:
            return None

    def get_all_tasks(self) -> TaskStore | None:
        return self._tasks

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None

        updates = task_update.model_dump(exclude_unset=True)
        updated_task = task.model_copy(update=updates)

        self._tasks[task_id] = updated_task
        return updated_task

    def delete_task(self, task_id: int) -> bool:
        deleted_task = self._tasks.pop(task_id, None)
        if deleted_task is None:
            return False
        return True
