import pytest
from httpx import AsyncClient

from tests.helpers import assert_task_shape


@pytest.mark.anyio
async def test_get_all_tasks_starts_empty(client: AsyncClient) -> None:
    response = await client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_create_and_get_task_in_memory(client: AsyncClient) -> None:
    create_response = await client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Cover current endpoints"},
    )

    assert create_response.status_code == 200
    created_task = create_response.json()
    assert_task_shape(
        created_task,
        expected_id=1,
        expected_title="Write tests",
        expected_description="Cover current endpoints",
    )

    get_response = await client.get("/tasks/1")

    assert get_response.status_code == 200
    assert get_response.json() == created_task


@pytest.mark.anyio
async def test_get_all_tasks_returns_created_tasks(client: AsyncClient) -> None:
    await client.post("/tasks", json={"title": "First task", "description": "one"})
    await client.post("/tasks", json={"title": "Second task", "description": "two"})

    response = await client.get("/tasks")

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert_task_shape(
        tasks[0],
        expected_id=1,
        expected_title="First task",
        expected_description="one",
    )
    assert_task_shape(
        tasks[1],
        expected_id=2,
        expected_title="Second task",
        expected_description="two",
    )


@pytest.mark.anyio
async def test_update_task_in_memory(client: AsyncClient) -> None:
    await client.post(
        "/tasks", json={"title": "Initial title", "description": "Initial"}
    )

    update_response = await client.patch("/tasks/1", json={"description": "Updated"})

    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert_task_shape(
        updated_task,
        expected_id=1,
        expected_title="Initial title",
        expected_description="Updated",
    )

    get_response = await client.get("/tasks/1")

    assert get_response.status_code == 200
    fetched_task = get_response.json()
    assert fetched_task["description"] == "Updated"
    assert fetched_task["updated_at"] == updated_task["updated_at"]


@pytest.mark.anyio
async def test_delete_task_in_memory(client: AsyncClient) -> None:
    await client.post("/tasks", json={"title": "Disposable", "description": None})

    delete_response = await client.delete("/tasks/1")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get("/tasks/1")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Task with id 1 not found"}


@pytest.mark.anyio
async def test_delete_all_tasks_in_memory(client: AsyncClient) -> None:
    await client.post("/tasks", json={"title": "First", "description": "one"})
    await client.post("/tasks", json={"title": "Second", "description": "two"})

    delete_response = await client.delete("/tasks")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    list_response = await client.get("/tasks")

    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.anyio
async def test_get_task_returns_not_found_for_missing_id(client: AsyncClient) -> None:
    response = await client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 999 not found"}


@pytest.mark.anyio
async def test_update_task_returns_not_found_for_missing_id(
    client: AsyncClient,
) -> None:
    response = await client.patch("/tasks/999", json={"title": "Missing"})

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cannot update task with id 999: task not found"
    }


@pytest.mark.anyio
async def test_delete_task_returns_not_found_for_missing_id(
    client: AsyncClient,
) -> None:
    response = await client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cannot delete task with id 999: task not found"
    }
