from logging import getLogger
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.task import create_task_router
from app.db.repository import TaskRepository
from app.db.storage import JSONFileTaskStorage
from app.models.storage import StorageError

logger = getLogger()

"""
This is a simple Tasks API to learn and practice FastAPI
"""


def create_app(data_file_path: Path | None = None) -> FastAPI:
    app = FastAPI()

    storage = JSONFileTaskStorage(data_file_path=data_file_path)
    session = TaskRepository(storage=storage)
    app.include_router(create_task_router(session=session))

    @app.exception_handler(StorageError)
    async def storage_error_handler(
        request: Request, exc: StorageError
    ) -> JSONResponse:
        logger.exception(
            f"Storage error while handling {request.url.path}",
            exc_info=exc,
        )

        content = {"detail": "Internal storage error"}

        if app.debug:
            content["error"] = str(exc)
            if exc.__cause__ is not None:
                content["cause"] = str(exc.__cause__)

        return JSONResponse(status_code=500, content=content)

    return app


app = create_app()
