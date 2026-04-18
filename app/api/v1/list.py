from logging import getLogger

from app.db.list_repository import TaskListRepository
from app.models.list import TaskList, TaskListCreate, TaskListUpdate
from fastapi import APIRouter, HTTPException, status

logger = getLogger(__name__)


def create_task_list_router(
    list_repo: TaskListRepository,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/lists", tags=["Lists"])

    @router.get("/health", response_model=dict[str, str])
    async def check_health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/", response_model=list[TaskList])
    async def get_all_task_lists() -> list[TaskList]:
        return list_repo.get_all_task_lists()

    @router.get("/{task_list_id}", response_model=TaskList)
    async def get_task_list(task_list_id: int) -> TaskList:
        task_list = list_repo.get_task_list_by_id(task_list_id)
        if task_list is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TaskList with id {task_list_id} not found",
            )
        return task_list

    @router.post("/", status_code=status.HTTP_201_CREATED, response_model=TaskList)
    async def create_task_list(task_list: TaskListCreate) -> TaskList:
        return list_repo.create_task_list(task_list)

    @router.patch("/{task_list_id}", response_model=TaskList)
    async def update_task_list(
        task_list_id: int,
        task_list_update: TaskListUpdate,
    ) -> TaskList:
        task_list = list_repo.update_task_list(task_list_id, task_list_update)
        if task_list is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Cannot update TaskList with id {task_list_id}: "
                    "task list not found"
                ),
            )
        return task_list

    @router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_all_task_lists() -> None:
        list_repo.delete_all_task_lists()

    @router.delete("/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_task_list(task_list_id: int) -> None:
        if not list_repo.delete_task_list(task_list_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Cannot delete TaskList with id {task_list_id}: "
                    "task list not found"
                ),
            )

    return router
