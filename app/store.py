from app.schemas import Task, TaskCreate, TaskUpdate


class Store:
    # SINGLETON PATTERN
    # So we can only have one Store
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Store":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, storage) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.tasks: dict[int, Task] = {}
        self._next_id = 1
        self.storage = storage

    def _get_next_id(self) -> int:
        id = self._next_id
        self._next_id += 1
        return id

    def create_task(self, task_create: TaskCreate) -> Task:
        id = self._get_next_id()
        task = Task(**task_create.model_dump(), id=id)
        self.tasks[id] = task
        return task

    def get_task_by_id(self, task_id: int) -> Task | None:
        return self.tasks.get(task_id)

    def get_all_tasks(self):
        return self.tasks

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task | None:
        task = self.tasks.get(task_id)
        if task is None:
            return None

        updates = task_update.model_dump(exclude_unset=True)
        updated_task = task.model_copy(update=updates)

        self.tasks[task_id] = updated_task
        return updated_task

    def delete_task(self, task_id: int) -> bool:
        deleted_task = self.tasks.pop(task_id, None)
        if deleted_task is None:
            return False
        return True
