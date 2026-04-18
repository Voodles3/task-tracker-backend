import logging
from pathlib import Path

from app.api.v1.list import create_task_list_router
from app.api.v1.task import create_task_router
from app.core.errors import ListHasTasksError, ListNotFoundError, StorageError
from app.core.logging import setup_logging
from app.db.context import RepositoryContext
from app.db.list_repository import TaskListRepository
from app.db.storage import JSONFileStorage
from app.db.task_repository import TaskRepository
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

setup_logging()
logger = logging.getLogger(__name__)

"""
This is a simple Tasks API to learn and practice FastAPI
"""


def create_app(data_file_path: Path | None = None) -> FastAPI:
    app = FastAPI()

    storage = JSONFileStorage(data_file_path=data_file_path)
    context = RepositoryContext(storage)

    task_repository = TaskRepository(context=context)
    list_repository = TaskListRepository(context=context)

    app.include_router(create_task_router(task_repo=task_repository))
    app.include_router(create_task_list_router(list_repo=list_repository))

    @app.exception_handler(StorageError)
    async def storage_error_handler(request: Request, e: StorageError) -> JSONResponse:
        logger.exception(
            f"Storage error while handling {request.url.path}",
            exc_info=e,
        )

        content = {"detail": "Internal storage error"}

        if app.debug:
            content["error"] = str(e)
            if e.__cause__ is not None:
                content["cause"] = str(e.__cause__)

        return JSONResponse(status_code=500, content=content)

    @app.exception_handler(ListNotFoundError)
    async def list_not_found_handler(
        request: Request,
        e: ListNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": f"TaskList with id {e.list_id} not found"},
        )

    @app.exception_handler(ListHasTasksError)
    async def list_has_tasks_handler(
        request: Request, e: ListHasTasksError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "detail": f"Cannot delete TaskList with id {e.list_id}: "
                "task list has tasks"
            },
        )

    return app


app = create_app()
