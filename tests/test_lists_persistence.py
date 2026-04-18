import json
from pathlib import Path

import pytest
from app.main import create_app
from httpx import AsyncClient
from tests.helpers import (
    assert_task_list_shape,
    create_test_client,
    get_tasks_from_response,
)


def build_restarted_client(persistence_file_path: Path) -> AsyncClient:
    restarted_app = create_app(data_file_path=persistence_file_path)
    return create_test_client(restarted_app)


@pytest.mark.anyio
async def test_create_task_list_persists_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    create_response = await persistence_client.post(
        "/api/v1/lists/",
        json={"name": "Work"},
    )
    assert create_response.status_code == 201

    async with build_restarted_client(restartable_file_path) as restarted_client:
        get_response = await restarted_client.get("/api/v1/lists/1")

    assert get_response.status_code == 200
    assert_task_list_shape(get_response.json(), expected_id=1, expected_name="Work")


@pytest.mark.anyio
async def test_updated_task_list_persists_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post("/api/v1/lists/", json={"name": "Work"})

    update_response = await persistence_client.patch(
        "/api/v1/lists/1",
        json={"name": "Deep Work"},
    )

    assert update_response.status_code == 200

    async with build_restarted_client(restartable_file_path) as restarted_client:
        get_response = await restarted_client.get("/api/v1/lists/1")

    assert get_response.status_code == 200
    assert_task_list_shape(
        get_response.json(),
        expected_id=1,
        expected_name="Deep Work",
    )


@pytest.mark.anyio
async def test_deleted_task_list_stays_deleted_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post("/api/v1/lists/", json={"name": "Disposable"})

    delete_response = await persistence_client.delete("/api/v1/lists/1")

    assert delete_response.status_code == 204

    async with build_restarted_client(restartable_file_path) as restarted_client:
        get_response = await restarted_client.get("/api/v1/lists/1")
        list_response = await restarted_client.get("/api/v1/lists/")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "TaskList with id 1 not found"}
    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.anyio
async def test_next_list_id_continues_after_restart(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post("/api/v1/lists/", json={"name": "First"})
    await persistence_client.post("/api/v1/lists/", json={"name": "Second"})

    async with build_restarted_client(restartable_file_path) as restarted_client:
        create_response = await restarted_client.post(
            "/api/v1/lists/",
            json={"name": "Third"},
        )

    assert create_response.status_code == 201
    assert_task_list_shape(
        create_response.json(),
        expected_id=3,
        expected_name="Third",
    )


@pytest.mark.anyio
async def test_task_list_relationship_persists_between_sessions(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    await persistence_client.post("/api/v1/lists/", json={"name": "Work"})
    await persistence_client.post(
        "/api/v1/tasks/",
        json={"title": "Persisted task", "list_id": 1},
    )

    async with build_restarted_client(restartable_file_path) as restarted_client:
        task_response = await restarted_client.get("/api/v1/tasks/1")
        list_tasks_response = await restarted_client.get(
            "/api/v1/tasks/",
            params={"list_id": "1"},
        )

    tasks = get_tasks_from_response(list_tasks_response.json())

    assert task_response.status_code == 200
    assert task_response.json()["list_id"] == 1
    assert list_tasks_response.status_code == 200
    assert [task["title"] for task in tasks] == ["Persisted task"]


@pytest.mark.anyio
async def test_create_task_list_writes_expected_json_file(
    persistence_client: AsyncClient,
    restartable_file_path: Path,
) -> None:
    create_response = await persistence_client.post(
        "/api/v1/lists/",
        json={"name": "Persisted list"},
    )

    assert create_response.status_code == 201
    assert restartable_file_path.exists()

    saved_payload = json.loads(restartable_file_path.read_text(encoding="utf-8"))
    task_list = saved_payload["lists"]["1"]

    assert saved_payload["schema_version"] == 2
    assert saved_payload["next_task_id"] == 1
    assert saved_payload["next_list_id"] == 2
    assert saved_payload["tasks"] == {}
    assert_task_list_shape(
        task_list,
        expected_id=1,
        expected_name="Persisted list",
    )
