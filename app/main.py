from logging import getLogger
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.persistence import JSONFileTaskStorage
from app.routes.tasks import router as task_router
from app.schemas.app import AppState
from app.schemas.storage import StorageError
from app.store import Store

logger = getLogger(__name__)

"""
This is a simple Tasks API to learn and practice FastAPI
"""


def create_app(data_file_path: Path | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(task_router)
    store = Store(storage=JSONFileTaskStorage(data_file_path))
    app.state.container = AppState(store=store)

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
