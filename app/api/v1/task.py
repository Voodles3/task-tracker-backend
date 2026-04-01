from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.repository import TaskRepository
from app.models.task import Task, TaskCreate, TaskUpdate

logger = getLogger(__name__)


def create_task_router(
    session: TaskRepository,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

    def get_task_repository() -> TaskRepository:
        return session

    @router.get("/health")
    async def check_health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/")
    async def get_all_tasks(
        service: TaskRepository = Depends(get_task_repository),
    ) -> list[Task]:
        tasks = service.get_all_tasks()
        return list(tasks.values())

    @router.get("/{task_id}")
    async def get_task(
        task_id: int, service: TaskRepository = Depends(get_task_repository)
    ) -> Task:
        task = service.get_task_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )
        return task

    @router.post("/", status_code=status.HTTP_201_CREATED)
    async def create_task(
        task: TaskCreate, service: TaskRepository = Depends(get_task_repository)
    ) -> Task:
        return service.create_task(task)

    @router.patch("/{task_id}")
    async def update_task(
        task_id: int,
        task_update: TaskUpdate,
        service: TaskRepository = Depends(get_task_repository),
    ) -> Task:
        task = service.update_task(task_id, task_update)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot update task with id {task_id}: task not found",
            )
        return task

    @router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_all_tasks(
        service: TaskRepository = Depends(get_task_repository),
    ) -> None:
        service.delete_all_tasks()

    @router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_task(
        task_id: int, service: TaskRepository = Depends(get_task_repository)
    ) -> None:
        if not service.delete_task(task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot delete task with id {task_id}: task not found",
            )

    return router
