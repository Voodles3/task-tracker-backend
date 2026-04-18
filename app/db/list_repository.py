from datetime import UTC, datetime
from logging import getLogger

from app.core.errors import ListHasTasksError, StorageError
from app.db.context import RepositoryContext
from app.models.list import TaskList, TaskListCreate, TaskListUpdate

logger = getLogger(__name__)


class TaskListRepository:
    def __init__(self, context: RepositoryContext) -> None:
        self._context = context

    def create_task_list(self, list_create: TaskListCreate) -> TaskList:
        """Creates and stores a new TaskList"""
        with self._context.lock:
            state = self._context.state
            cached_state = state.model_copy(deep=True)

            task_list_id = state.next_list_id
            now = datetime.now(UTC)
            task_list = TaskList(
                **list_create.model_dump(),
                id=task_list_id,
                created_at=now,
                updated_at=now,
            )
            state.lists[task_list_id] = task_list
            try:
                state.next_list_id += 1
                self._context.save()
            except Exception as e:
                # Rollback in-memory storage on a save failure
                self._context.state = cached_state
                raise StorageError("Error creating new task list") from e

            return task_list

    def get_task_list_by_id(self, task_list_id: int) -> TaskList | None:
        """Returns a single TaskList by ID"""
        with self._context.lock:
            state = self._context.state
            task_list = state.lists.get(task_list_id)
            return task_list.model_copy() if task_list is not None else None

    def get_all_task_lists(
        self,
    ) -> list[TaskList]:
        """Returns all TaskLists"""
        with self._context.lock:
            state = self._context.state

            return [task_list.model_copy() for task_list in state.lists.values()]

    def update_task_list(
        self, task_list_id: int, task_list_update: TaskListUpdate
    ) -> TaskList | None:
        """Updates a TaskList by ID"""
        with self._context.lock:
            state = self._context.state

            original_task_list = state.lists.get(task_list_id)
            if original_task_list is None:
                return None

            now = datetime.now(UTC)
            updates = task_list_update.model_dump(exclude_unset=True)
            updates["updated_at"] = now

            updated_task_list = original_task_list.model_copy(update=updates)

            state.lists[task_list_id] = updated_task_list
            try:
                self._context.save()
            except Exception as e:
                state.lists[task_list_id] = original_task_list
                raise StorageError(
                    f"Error updating task list with id {task_list_id}"
                ) from e

            return updated_task_list

    def delete_task_list(self, task_list_id: int) -> bool:
        """Deletes one TaskList and returns whether it existed."""
        with self._context.lock:
            state = self._context.state

            original_task_list = state.lists.get(task_list_id)
            if original_task_list is None:
                return False

            if any(task.list_id == task_list_id for task in state.tasks.values()):
                raise ListHasTasksError(task_list_id)

            state.lists.pop(task_list_id)

            try:
                self._context.save()
            except Exception as e:
                state.lists[task_list_id] = original_task_list
                raise StorageError("Failed to save task list deletion") from e
            return True

    def delete_all_task_lists(self) -> bool:
        """Deletes all TaskLists. Returns True if successful."""
        with self._context.lock:
            state = self._context.state

            for task_list_id in state.lists:
                if any(task.list_id == task_list_id for task in state.tasks.values()):
                    raise ListHasTasksError(task_list_id)

            original_task_lists = state.lists.copy()
            state.lists.clear()

            try:
                self._context.save()
            except Exception as e:
                state.lists = original_task_lists
                raise StorageError("Failed to save all task lists deletion") from e
            return True
