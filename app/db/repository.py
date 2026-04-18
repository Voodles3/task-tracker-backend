from collections.abc import Callable
from datetime import UTC, datetime
from logging import getLogger
from operator import attrgetter

from app.db.context import RepositoryContext
from app.models.storage import (
    StorageError,
)
from app.models.task import (
    GetTasksResult,
    Order,
    SortBy,
    Task,
    TaskCreate,
    TaskQueryParams,
    TaskUpdate,
    default_sort_order,
)
from pydantic import AwareDatetime

logger = getLogger(__name__)


class TaskRepository:
    def __init__(self, context: RepositoryContext) -> None:
        self._context = context

    def create_task(self, task_create: TaskCreate) -> Task:
        """Creates and stores a new Task"""
        with self._context.lock:
            state = self._context.state
            cached_state = state.model_copy(deep=True)

            task_id = state.next_task_id
            now = datetime.now(UTC)
            task = Task(
                **task_create.model_dump(),
                id=task_id,
                created_at=now,
                updated_at=now,
            )
            state.tasks[task_id] = task
            try:
                state.next_task_id += 1
                self._context.save()
            except Exception as e:
                # Rollback in-memory storage on a save failure
                self._context.state = cached_state
                raise StorageError("Error creating new task") from e

            return task

    def get_task_by_id(self, task_id: int) -> Task | None:
        """Returns a single Task by ID"""
        with self._context.lock:
            state = self._context.state
            task = state.tasks.get(task_id)
            return task.model_copy() if task is not None else None

    def get_all_tasks(
        self,
        query_params: TaskQueryParams | None = None,
    ) -> GetTasksResult:
        """Returns filtered, sorted, and paginated tasks with result metadata."""
        with self._context.lock:
            state = self._context.state

            if query_params is None:
                query_params = TaskQueryParams()

            # Get all tasks matching basic query params
            tasks = [
                task.model_copy()
                for task in state.tasks.values()
                if (
                    self._matches_query_params(
                        task=task,
                        query_params=query_params,
                    )
                )
            ]

            # Sort tasks by sort key in specified order
            sort_key = self._get_sort_key(query_params)

            order = query_params.order or default_sort_order[query_params.sort_by]
            order_reverse = order.value == Order.DESC.value

            tasks.sort(key=sort_key, reverse=order_reverse)

            total = len(tasks)

            # Apply limit and offset to get desired subset
            limit = query_params.limit
            offset = query_params.offset
            end = limit + offset
            tasks = tasks[offset:end]

            count = len(tasks)

            return GetTasksResult(
                total=total, count=count, limit=limit, offset=offset, tasks=tasks
            )

    def _get_sort_key(
        self, query_params: TaskQueryParams
    ) -> Callable[[Task], AwareDatetime | int | str]:
        if query_params.sort_by is SortBy.DUE_DATE:
            return lambda task: task.due_date or datetime.max.replace(tzinfo=UTC)
        elif query_params.sort_by is SortBy.PRIORITY:
            return lambda task: task.priority.sort_order
        else:
            return attrgetter(query_params.sort_by.value)

    def _matches_query_params(
        self,
        task: Task,
        query_params: TaskQueryParams,
    ) -> bool:
        """Checks if a task matches the given filters.
        Returns True if the task matches all non-None filters."""

        completed = query_params.completed
        priority = query_params.priority
        due_before = query_params.due_before
        due_after = query_params.due_after
        query = query_params.q

        if completed is not None and task.completed != completed:
            return False
        if priority is not None and task.priority != priority:
            return False

        if not self._matches_query(task, query):
            return False

        return self._matches_due_dates(task, due_before, due_after)

    def _matches_query(self, task: Task, query: str | None) -> bool:
        if query is None or not query.strip():
            return True

        query = query.strip().casefold()
        searchable_text = task.title.casefold()
        if task.description is not None:
            searchable_text += f"\n{task.description.casefold()}"

        return query in searchable_text

    def _matches_due_dates(
        self,
        task: Task,
        due_before: AwareDatetime | None,
        due_after: AwareDatetime | None,
    ) -> bool:
        due_date = task.due_date
        if due_date is None:
            return due_before is None and due_after is None

        if due_before is not None and due_date >= due_before:
            return False

        return due_after is None or due_date > due_after

    def update_task(self, task_id: int, task_update: TaskUpdate) -> Task | None:
        """Updates a Task by ID"""
        with self._context.lock:
            state = self._context.state

            original_task = state.tasks.get(task_id)
            if original_task is None:
                return None

            now = datetime.now(UTC)
            updates = task_update.model_dump(exclude_unset=True)
            updates["updated_at"] = now
            if "due_date" in updates:
                updates["due_date"] = (
                    updates["due_date"].astimezone(UTC)
                    if updates["due_date"] is not None
                    else None
                )

            if updates.get("completed") is True and original_task.completed is False:
                updates["completed_at"] = now
            if updates.get("completed") is False:
                updates["completed_at"] = None

            updated_task = original_task.model_copy(update=updates)

            state.tasks[task_id] = updated_task
            try:
                self._context.save()
            except Exception as e:
                state.tasks[task_id] = original_task
                raise StorageError(f"Error updating task with id {task_id}") from e

            return updated_task

    def delete_task(self, task_id: int) -> bool:
        """Deletes one task and returns whether it existed."""
        with self._context.lock:
            state = self._context.state

            original_task = state.tasks.pop(task_id, None)
            if original_task is None:
                return False

            try:
                self._context.save()
            except Exception as e:
                state.tasks[task_id] = original_task
                raise StorageError("Failed to save task deletion") from e
            return True

    def delete_all_tasks(self) -> bool:
        """Deletes all Tasks. Returns True if successful."""
        with self._context.lock:
            state = self._context.state

            original_tasks = state.tasks.copy()
            state.tasks.clear()

            try:
                self._context.save()
            except Exception as e:
                state.tasks = original_tasks
                raise StorageError("Failed to save all tasks deletion") from e
            return True
