from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from httpx import AsyncClient

from app.main import create_app
from tests.helpers import create_test_client


@pytest.fixture
def isolated_file_path(tmp_path) -> Generator[Path, None, None]:
    path = tmp_path / "temp_tasks.json"
    yield path
    path.unlink(missing_ok=True)


@pytest.fixture
def restartable_file_path(tmp_path) -> Path:
    return tmp_path / "tasks.json"


@pytest.fixture
async def client(isolated_file_path) -> AsyncGenerator[AsyncClient, None]:
    app = create_app(data_file_path=isolated_file_path)
    async with create_test_client(app) as test_client:
        yield test_client


@pytest.fixture
async def persistence_client(
    restartable_file_path,
) -> AsyncGenerator[AsyncClient, None]:
    app = create_app(data_file_path=restartable_file_path)
    async with create_test_client(app) as test_client:
        yield test_client
