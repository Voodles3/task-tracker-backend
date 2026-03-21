import pytest


@pytest.mark.anyio
async def test_get_all_tasks_starts_empty(client):
    response = await client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_create_and_get_task_in_memory(client):
    create_response = await client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Cover current endpoints"},
    )

    assert create_response.status_code == 200
    created_task = create_response.json()
    assert created_task == {
        "id": 1,
        "title": "Write tests",
        "description": "Cover current endpoints",
    }

    get_response = await client.get("/tasks/1")

    assert get_response.status_code == 200
    assert get_response.json() == created_task


@pytest.mark.anyio
async def test_get_all_tasks_returns_created_tasks(client):
    await client.post("/tasks", json={"title": "First task", "description": "one"})
    await client.post("/tasks", json={"title": "Second task", "description": "two"})

    response = await client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "First task", "description": "one"},
        {"id": 2, "title": "Second task", "description": "two"},
    ]


@pytest.mark.anyio
async def test_update_task_in_memory(client):
    await client.post(
        "/tasks", json={"title": "Initial title", "description": "Initial"}
    )

    update_response = await client.patch("/tasks/1", json={"description": "Updated"})

    assert update_response.status_code == 200
    assert update_response.json() == {
        "id": 1,
        "title": "Initial title",
        "description": "Updated",
    }

    get_response = await client.get("/tasks/1")

    assert get_response.status_code == 200
    assert get_response.json()["description"] == "Updated"


@pytest.mark.anyio
async def test_delete_task_in_memory(client):
    await client.post("/tasks", json={"title": "Disposable", "description": None})

    delete_response = await client.delete("/tasks/1")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get("/tasks/1")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Task with id 1 not found"}


@pytest.mark.anyio
async def test_get_task_returns_not_found_for_missing_id(client):
    response = await client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 999 not found"}


@pytest.mark.anyio
async def test_update_task_returns_not_found_for_missing_id(client):
    response = await client.patch("/tasks/999", json={"title": "Missing"})

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cannot update task with id 999: task not found"
    }


@pytest.mark.anyio
async def test_delete_task_returns_not_found_for_missing_id(client):
    response = await client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cannot delete task with id 999: task not found"
    }
