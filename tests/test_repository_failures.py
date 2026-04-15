from datetime import UTC, datetime

import pytest
from app.db.repository import TaskRepository
from app.models.storage import JSONSaveData, StorageAdapter, StorageError, TaskMap
from app.models.task import TaskCreate, TaskQueryParams, TaskUpdate


class ControlledStorage(StorageAdapter):
    def __init__(
        self,
        *,
        data: JSONSaveData | None = None,
        fail_on_save: bool = False,
    ) -> None:
        empty_tasks: TaskMap = {}
        self._data: JSONSaveData = (
            data if data is not None else JSONSaveData(next_id=1, tasks=empty_tasks)
        )
        self._fail_on_save: bool = fail_on_save

    def set_fail_on_save(self, value: bool) -> None:
        self._fail_on_save = value

    def save(self, data: JSONSaveData) -> None:
        if self._fail_on_save:
            raise RuntimeError("forced save failure")
        self._data = data.model_copy(deep=True)

    def load(self) -> JSONSaveData:
        return self._data.model_copy(deep=True)


def _empty_query_params() -> TaskQueryParams:
    return TaskQueryParams(
        completed=None, priority=None, due_before=None, due_after=None, q=None
    )


def _build_seeded_repo() -> tuple[TaskRepository, ControlledStorage]:
    storage = ControlledStorage()
    repository = TaskRepository(storage=storage)
    repository.create_task(TaskCreate(title="First", description="one"))
    repository.create_task(TaskCreate(title="Second", description="two"))
    return repository, storage


def test_create_task_rolls_back_state_when_save_fails() -> None:
    storage = ControlledStorage(fail_on_save=True)
    repository = TaskRepository(storage=storage)

    with pytest.raises(StorageError, match="Error creating new task"):
        repository.create_task(TaskCreate(title="new", description="task"))

    all_tasks = repository.get_all_tasks(_empty_query_params())
    assert len(all_tasks) == 0

    # Ensure next_id rollback happened: first successful create should still be ID 1.
    storage.set_fail_on_save(False)
    created_task = repository.create_task(TaskCreate(title="works", description=None))
    assert created_task.id == 1


def test_update_task_rolls_back_state_when_save_fails() -> None:
    repository, storage = _build_seeded_repo()
    original_task = repository.get_task_by_id(1)
    assert original_task is not None

    storage.set_fail_on_save(True)
    with pytest.raises(StorageError, match="Error updating task with id 1"):
        repository.update_task(1, TaskUpdate(title="Updated"))

    task_after_failure = repository.get_task_by_id(1)
    assert task_after_failure == original_task


def test_delete_task_rolls_back_state_when_save_fails() -> None:
    repository, storage = _build_seeded_repo()
    storage.set_fail_on_save(True)

    with pytest.raises(StorageError, match="Failed to save task deletion"):
        repository.delete_task(1)

    remaining = repository.get_all_tasks(_empty_query_params())
    assert sorted(remaining.keys()) == [1, 2]


def test_delete_all_tasks_rolls_back_state_when_save_fails() -> None:
    repository, storage = _build_seeded_repo()
    storage.set_fail_on_save(True)

    with pytest.raises(StorageError, match="Failed to save all tasks deletion"):
        repository.delete_all_tasks()

    remaining = repository.get_all_tasks(_empty_query_params())
    assert sorted(remaining.keys()) == [1, 2]


def test_update_task_allows_explicit_due_date_clearing() -> None:
    repository = TaskRepository(storage=ControlledStorage())
    created = repository.create_task(
        TaskCreate(
            title="has due date",
            description=None,
            due_date=datetime(2026, 7, 1, tzinfo=UTC),
        )
    )
    assert created.due_date is not None

    updated = repository.update_task(created.id, TaskUpdate(due_date=None))
    assert updated is not None
    assert updated.due_date is None
