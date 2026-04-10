from pathlib import Path

import pytest
from app.main import create_app
from tests.helpers import create_test_client


@pytest.mark.anyio
async def test_separate_apps_do_not_share_in_memory_state(
    tmp_path: Path,
) -> None:
    first_file_path = tmp_path / "first_tasks.json"
    second_file_path = tmp_path / "second_tasks.json"

    first_app = create_app(data_file_path=first_file_path)
    second_app = create_app(data_file_path=second_file_path)

    async with create_test_client(first_app) as first_client:
        create_response = await first_client.post(
            "/api/v1/tasks/",
            json={"title": "First app task", "description": "one"},
        )

        assert create_response.status_code == 201

    async with create_test_client(second_app) as second_client:
        list_response = await second_client.get("/api/v1/tasks/")

    assert list_response.status_code == 200
    assert list_response.json() == []
