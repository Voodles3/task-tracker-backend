from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.persistence import JSONFileTaskStorage
from app.schemas import StorageError, Task, TaskCreate, TaskUpdate
from app.store import Store

"""
This is a simple Tasks API to learn and practice FastAPI
"""


def create_app(data_file_path: Path | None = None) -> FastAPI:
    ### App config
    app = FastAPI()
    store = Store(storage=JSONFileTaskStorage(data_file_path))

    ### ------------------- ###

    ### Endpoints
    @app.exception_handler(StorageError)
    async def storage_error_handler(request: Request, exc: StorageError):
        return JSONResponse(
            status_code=500, content={"detail": "Internal storage error"}
        )

    @app.get("/")
    async def root():
        return {"You are at root": True}

    @app.get("/health")
    async def check_health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/tasks")
    async def get_all_tasks() -> list[Task]:
        tasks = store.get_all_tasks()
        return list(tasks.values())

    @app.get("/tasks/{task_id}")
    async def get_task(task_id: int) -> Task:
        task = store.get_task_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )
        return task

    @app.post("/tasks")
    async def create_task(task: TaskCreate) -> Task:
        return store.create_task(task)

    @app.patch("/tasks/{task_id}")
    async def update_task(task_id: int, task_update: TaskUpdate) -> Task:
        task = store.update_task(task_id, task_update)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot update task with id {task_id}: task not found",
            )
        return task

    @app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_task(task_id: int) -> None:
        if not store.delete_task(task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot delete task with id {task_id}: task not found",
            )

    return app


app = create_app()
