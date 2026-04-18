import pytest
from httpx import AsyncClient
from tests.helpers import assert_task_list_shape, get_tasks_from_response


@pytest.mark.anyio
async def test_get_all_task_lists_starts_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/lists/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_create_and_get_task_list_in_memory(client: AsyncClient) -> None:
    create_response = await client.post("/api/v1/lists/", json={"name": " Work "})

    assert create_response.status_code == 201
    created_list = create_response.json()
    assert_task_list_shape(created_list, expected_id=1, expected_name="Work")

    get_response = await client.get("/api/v1/lists/1")

    assert get_response.status_code == 200
    assert get_response.json() == created_list


@pytest.mark.anyio
async def test_get_all_task_lists_returns_created_lists(client: AsyncClient) -> None:
    await client.post("/api/v1/lists/", json={"name": "Personal"})
    await client.post("/api/v1/lists/", json={"name": "Learning"})

    response = await client.get("/api/v1/lists/")

    assert response.status_code == 200
    task_lists = response.json()
    assert len(task_lists) == 2
    assert_task_list_shape(task_lists[0], expected_id=1, expected_name="Personal")
    assert_task_list_shape(task_lists[1], expected_id=2, expected_name="Learning")


@pytest.mark.anyio
async def test_update_task_list_in_memory(client: AsyncClient) -> None:
    await client.post("/api/v1/lists/", json={"name": "Personal"})

    update_response = await client.patch("/api/v1/lists/1", json={"name": " Home "})

    assert update_response.status_code == 200
    updated_list = update_response.json()
    assert_task_list_shape(updated_list, expected_id=1, expected_name="Home")
    assert updated_list["updated_at"] >= updated_list["created_at"]


@pytest.mark.anyio
async def test_task_list_name_validation_and_uniqueness(
    client: AsyncClient,
) -> None:
    blank_response = await client.post("/api/v1/lists/", json={"name": "   "})

    assert blank_response.status_code == 422
    assert blank_response.json()["detail"]

    create_response = await client.post("/api/v1/lists/", json={"name": "Work"})
    duplicate_response = await client.post("/api/v1/lists/", json={"name": " work "})

    assert create_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "TaskList with name work already exists"
    }


@pytest.mark.anyio
async def test_update_task_list_rejects_duplicate_but_allows_same_name(
    client: AsyncClient,
) -> None:
    await client.post("/api/v1/lists/", json={"name": "Work"})
    await client.post("/api/v1/lists/", json={"name": "Personal"})

    same_name_response = await client.patch("/api/v1/lists/1", json={"name": " work "})
    duplicate_response = await client.patch("/api/v1/lists/2", json={"name": "Work"})

    assert same_name_response.status_code == 200
    assert same_name_response.json()["name"] == "work"
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "TaskList with name Work already exists"
    }


@pytest.mark.anyio
async def test_delete_task_list_in_memory(client: AsyncClient) -> None:
    await client.post("/api/v1/lists/", json={"name": "Disposable"})

    delete_response = await client.delete("/api/v1/lists/1")
    get_response = await client.get("/api/v1/lists/1")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "TaskList with id 1 not found"}


@pytest.mark.anyio
async def test_delete_all_task_lists_in_memory(client: AsyncClient) -> None:
    await client.post("/api/v1/lists/", json={"name": "First"})
    await client.post("/api/v1/lists/", json={"name": "Second"})

    delete_response = await client.delete("/api/v1/lists/")
    list_response = await client.get("/api/v1/lists/")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.anyio
async def test_task_list_missing_id_returns_not_found(client: AsyncClient) -> None:
    get_response = await client.get("/api/v1/lists/999")
    update_response = await client.patch("/api/v1/lists/999", json={"name": "Missing"})
    delete_response = await client.delete("/api/v1/lists/999")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "TaskList with id 999 not found"}
    assert update_response.status_code == 404
    assert update_response.json() == {
        "detail": "Cannot update TaskList with id 999: task list not found"
    }
    assert delete_response.status_code == 404
    assert delete_response.json() == {
        "detail": "Cannot delete TaskList with id 999: task list not found"
    }


@pytest.mark.anyio
async def test_task_list_delete_rejects_lists_with_tasks(
    client: AsyncClient,
) -> None:
    await client.post("/api/v1/lists/", json={"name": "Work"})
    await client.post("/api/v1/tasks/", json={"title": "List task", "list_id": 1})

    delete_response = await client.delete("/api/v1/lists/1")
    delete_all_response = await client.delete("/api/v1/lists/")

    assert delete_response.status_code == 409
    assert delete_response.json() == {
        "detail": "Cannot delete TaskList with id 1: task list has tasks"
    }
    assert delete_all_response.status_code == 409
    assert delete_all_response.json() == {
        "detail": "Cannot delete TaskList with id 1: task list has tasks"
    }


@pytest.mark.anyio
async def test_task_list_id_on_task_create_update_and_filter(
    client: AsyncClient,
) -> None:
    await client.post("/api/v1/lists/", json={"name": "Work"})
    await client.post("/api/v1/lists/", json={"name": "Personal"})

    create_response = await client.post(
        "/api/v1/tasks/",
        json={"title": "Work task", "description": "one", "list_id": 1},
    )
    await client.post(
        "/api/v1/tasks/",
        json={"title": "Personal task", "description": "two", "list_id": 2},
    )
    await client.post(
        "/api/v1/tasks/",
        json={"title": "Inbox task", "description": "three"},
    )

    assert create_response.status_code == 201
    assert create_response.json()["list_id"] == 1

    list_response = await client.get("/api/v1/tasks/", params={"list_id": "1"})
    tasks = get_tasks_from_response(list_response.json())

    assert list_response.status_code == 200
    assert [task["title"] for task in tasks] == ["Work task"]

    missing_list_response = await client.get(
        "/api/v1/tasks/",
        params={"list_id": "999"},
    )
    missing_list_tasks = get_tasks_from_response(missing_list_response.json())

    assert missing_list_response.status_code == 200
    assert missing_list_tasks == []

    move_response = await client.patch("/api/v1/tasks/1", json={"list_id": 2})
    clear_response = await client.patch("/api/v1/tasks/1", json={"list_id": None})

    assert move_response.status_code == 200
    assert move_response.json()["list_id"] == 2
    assert clear_response.status_code == 200
    assert clear_response.json()["list_id"] is None


@pytest.mark.anyio
async def test_task_list_id_rejects_missing_list_on_task_create_and_update(
    client: AsyncClient,
) -> None:
    await client.post("/api/v1/tasks/", json={"title": "Existing task"})

    create_response = await client.post(
        "/api/v1/tasks/",
        json={"title": "Missing list task", "list_id": 999},
    )
    update_response = await client.patch("/api/v1/tasks/1", json={"list_id": 999})

    assert create_response.status_code == 404
    assert create_response.json() == {"detail": "TaskList with id 999 not found"}
    assert update_response.status_code == 404
    assert update_response.json() == {"detail": "TaskList with id 999 not found"}
