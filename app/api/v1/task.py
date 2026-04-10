from logging import getLogger

from app.db.repository import TaskRepository
from app.models.task import Task, TaskCreate, TaskQueryParams, TaskUpdate
from fastapi import APIRouter, Depends, HTTPException, status

logger = getLogger(__name__)


def create_task_router(
    session: TaskRepository,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

    @router.get("/health", response_model=dict[str, str])
    async def check_health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/", response_model=list[Task])
    async def get_all_tasks(query_params: TaskQueryParams = Depends()) -> list[Task]:
        tasks = session.get_all_tasks(query_params)
        return list(tasks.values())

    @router.get("/{task_id}", response_model=Task)
    async def get_task(task_id: int) -> Task:
        task = session.get_task_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )
        return task

    @router.post("/", status_code=status.HTTP_201_CREATED, response_model=Task)
    async def create_task(task: TaskCreate) -> Task:
        return session.create_task(task)

    @router.patch("/{task_id}", response_model=Task)
    async def update_task(
        task_id: int,
        task_update: TaskUpdate,
    ) -> Task:
        task = session.update_task(task_id, task_update)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot update task with id {task_id}: task not found",
            )
        return task

    @router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_all_tasks() -> None:
        session.delete_all_tasks()

    @router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_task(task_id: int) -> None:
        if not session.delete_task(task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot delete task with id {task_id}: task not found",
            )

    return router
