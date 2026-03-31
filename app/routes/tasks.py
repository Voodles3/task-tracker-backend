from logging import getLogger
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.app import AppState
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.store import Store

logger = getLogger(__name__)


router = APIRouter(prefix="/api/v1/tasks")


def get_store(request: Request) -> Store:
    container = cast(AppState, request.app.state.container)
    return container.store


@router.get("/health")
async def check_health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/")
async def get_all_tasks(store: Store = Depends(get_store)) -> list[Task]:
    tasks = store.get_all_tasks()
    return list(tasks.values())


@router.get("/{task_id}")
async def get_task(task_id: int, store: Store = Depends(get_store)) -> Task:
    task = store.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, store: Store = Depends(get_store)) -> Task:
    return store.create_task(task)


@router.patch("/{task_id}")
async def update_task(
    task_id: int, task_update: TaskUpdate, store: Store = Depends(get_store)
) -> Task:
    task = store.update_task(task_id, task_update)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot update task with id {task_id}: task not found",
        )
    return task


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_tasks(store: Store = Depends(get_store)) -> None:
    store.delete_all_tasks()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, store: Store = Depends(get_store)) -> None:
    if not store.delete_task(task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot delete task with id {task_id}: task not found",
        )
