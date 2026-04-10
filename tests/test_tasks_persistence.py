import json
from pathlib import Path

import pytest
from app.main import create_app
from httpx import AsyncClient
from tests.helpers import assert_task_shape, create_test_client


def build_restarted_client(persistence_file_path: Path) -> AsyncClient:
    restarted_app = create_app(data_file_path=persistence_file_path)
    return create_test_client(restarted_app)


@pytest.mark.anyio
async def test_create_task_persists_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    create_response = await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "Write tests", "description": "persist me"},
    )
    assert create_response.status_code == 201

    async with build_restarted_client(restartable_file_path) as restarted_client:
        get_response = await restarted_client.get("/api/v1/tasks/1")

    assert get_response.status_code == 200
    assert_task_shape(
        get_response.json(),
        expected_id=1,
        expected_title="Write tests",
        expected_description="persist me",
    )


@pytest.mark.anyio
async def test_updated_task_persists_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "Original title", "description": "Original description"},
    )

    update_response = await persistence_client.patch(
        "/api/v1/tasks/1",
        json={"title": "Updated title", "description": "Updated description"},
    )

    assert update_response.status_code == 200

    async with build_restarted_client(restartable_file_path) as restarted_client:
        get_response = await restarted_client.get("/api/v1/tasks/1")

    assert get_response.status_code == 200
    assert_task_shape(
        get_response.json(),
        expected_id=1,
        expected_title="Updated title",
        expected_description="Updated description",
    )


@pytest.mark.anyio
async def test_completed_at_persists_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "Complete me", "description": "persist completion"},
    )

    complete_response = await persistence_client.patch(
        "/api/v1/tasks/1",
        json={"completed": True},
    )

    assert complete_response.status_code == 200
    completed_task = complete_response.json()
    assert completed_task["completed"] is True
    assert completed_task["completed_at"] is not None

    async with build_restarted_client(restartable_file_path) as restarted_client:
        get_response = await restarted_client.get("/api/v1/tasks/1")

    assert get_response.status_code == 200
    assert_task_shape(
        get_response.json(),
        expected_id=1,
        expected_title="Complete me",
        expected_description="persist completion",
        expected_completed=True,
        expected_completed_at=completed_task["completed_at"],
    )


@pytest.mark.anyio
async def test_deleted_task_stays_deleted_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "Disposable", "description": "Delete me"},
    )

    delete_response = await persistence_client.delete("/api/v1/tasks/1")

    assert delete_response.status_code == 204

    async with build_restarted_client(restartable_file_path) as restarted_client:
        get_response = await restarted_client.get("/api/v1/tasks/1")
        list_response = await restarted_client.get("/api/v1/tasks/")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Task with id 1 not found"}
    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.anyio
async def test_delete_all_tasks_stays_deleted_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "First", "description": "one"},
    )
    await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "Second", "description": "two"},
    )

    delete_response = await persistence_client.delete("/api/v1/tasks/")

    assert delete_response.status_code == 204

    async with build_restarted_client(restartable_file_path) as restarted_client:
        list_response = await restarted_client.get("/api/v1/tasks/")
        create_response = await restarted_client.post(
            "/api/v1/tasks/",
            json={"title": "Third", "description": "three"},
        )

    assert list_response.status_code == 200
    assert list_response.json() == []
    assert create_response.status_code == 201
    assert_task_shape(
        create_response.json(),
        expected_id=3,
        expected_title="Third",
        expected_description="three",
    )


@pytest.mark.anyio
async def test_next_id_continues_after_restart(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post(
        "/api/v1/tasks/", json={"title": "First", "description": "one"}
    )
    await persistence_client.post(
        "/api/v1/tasks/", json={"title": "Second", "description": "two"}
    )

    async with build_restarted_client(restartable_file_path) as restarted_client:
        create_response = await restarted_client.post(
            "/api/v1/tasks/",
            json={"title": "Third", "description": "three"},
        )

    assert create_response.status_code == 201
    assert_task_shape(
        create_response.json(),
        expected_id=3,
        expected_title="Third",
        expected_description="three",
    )


@pytest.mark.anyio
async def test_create_task_writes_expected_json_file(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    create_response = await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "Persisted task", "description": "written to disk"},
    )

    assert create_response.status_code == 201
    assert restartable_file_path.exists()

    saved_payload = json.loads(restartable_file_path.read_text(encoding="utf-8"))
    task = saved_payload["tasks"]["1"]

    assert saved_payload["next_id"] == 2
    assert_task_shape(
        task,
        expected_id=1,
        expected_title="Persisted task",
        expected_description="written to disk",
    )
