from fastapi import FastAPI, HTTPException, status
from app.schemas import Task, TaskCreate, TaskUpdate, TaskStore
from app.store import Store
from app.persistence import JSONFileTaskStorage

app = FastAPI()
store = Store(storage=JSONFileTaskStorage())


"""
This is a simple Tasks API to practice and learn FastAPI
"""


@app.get("/")
async def root():
    return {"You are at root": True}


@app.get("/health")
async def check_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks")
async def get_all_tasks() -> TaskStore:
    tasks = store.get_all_tasks()
    return tasks or {}


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
    print(type(task))
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
