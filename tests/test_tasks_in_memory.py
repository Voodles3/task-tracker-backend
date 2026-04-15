import pytest
from httpx import AsyncClient
from tests.helpers import assert_task_shape


async def _seed_query_param_tasks(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/tasks/",
        json={
            "title": "Completed high",
            "description": "done and high priority",
            "priority": "HIGH",
            "due_date": "2026-01-01T00:00:00Z",
        },
    )
    await client.patch("/api/v1/tasks/1", json={"completed": True})
    await client.post(
        "/api/v1/tasks/",
        json={
            "title": "Open low",
            "description": "open with low priority",
            "priority": "LOW",
            "due_date": "2026-02-01T00:00:00Z",
        },
    )
    await client.post(
        "/api/v1/tasks/",
        json={
            "title": "Open high later",
            "description": "open and high priority with later due date",
            "priority": "HIGH",
            "due_date": "2026-03-01T00:00:00Z",
        },
    )


@pytest.mark.anyio
async def test_get_all_tasks_starts_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/tasks/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_create_and_get_task_in_memory(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/tasks/",
        json={"title": "Write tests", "description": "Cover current endpoints"},
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    assert_task_shape(
        created_task,
        expected_id=1,
        expected_title="Write tests",
        expected_description="Cover current endpoints",
    )

    get_response = await client.get("/api/v1/tasks/1")

    assert get_response.status_code == 200
    assert get_response.json() == created_task


@pytest.mark.anyio
async def test_get_all_tasks_returns_created_tasks(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/tasks/", json={"title": "First task", "description": "one"}
    )
    await client.post(
        "/api/v1/tasks/", json={"title": "Second task", "description": "two"}
    )

    response = await client.get("/api/v1/tasks/")

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
async def test_get_all_tasks_filters_by_completed_query_param(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)

    response = await client.get("/api/v1/tasks/", params={"completed": "true"})

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == 1
    assert tasks[0]["title"] == "Completed high"
    assert tasks[0]["completed"] is True


@pytest.mark.anyio
async def test_get_all_tasks_filters_by_priority_query_param(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)

    response = await client.get("/api/v1/tasks/", params={"priority": "HIGH"})

    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [1, 3]
    assert [task["priority"] for task in tasks] == ["HIGH", "HIGH"]


@pytest.mark.anyio
async def test_get_all_tasks_filters_by_due_before_query_param(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)

    response = await client.get(
        "/api/v1/tasks/",
        params={"due_before": "2026-02-15T00:00:00Z"},
    )

    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [1, 2]
    assert [task["title"] for task in tasks] == ["Completed high", "Open low"]


@pytest.mark.anyio
async def test_get_all_tasks_filters_by_due_after_query_param(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)

    response = await client.get(
        "/api/v1/tasks/",
        params={"due_after": "2026-02-15T00:00:00Z"},
    )

    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [3]
    assert [task["title"] for task in tasks] == ["Open high later"]


@pytest.mark.anyio
async def test_get_all_tasks_excludes_tasks_without_due_date_when_due_filter_is_used(
    client: AsyncClient,
) -> None:
    await client.post(
        "/api/v1/tasks/",
        json={
            "title": "No due date",
            "description": "should not pass due-date filters",
            "priority": "MEDIUM",
        },
    )
    await client.post(
        "/api/v1/tasks/",
        json={
            "title": "Has due date",
            "description": "should pass due-date filters",
            "priority": "MEDIUM",
            "due_date": "2026-04-01T00:00:00Z",
        },
    )

    response = await client.get(
        "/api/v1/tasks/",
        params={"due_after": "2026-01-01T00:00:00Z"},
    )

    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [2]
    assert [task["title"] for task in tasks] == ["Has due date"]


@pytest.mark.anyio
async def test_get_all_tasks_filters_title_by_query(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)
    response = await client.get("/api/v1/tasks/", params={"q": "high laTe"})

    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [3]


@pytest.mark.anyio
async def test_get_all_tasks_not_filtered_with_blank_query(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)
    response = await client.get("/api/v1/tasks/", params={"q": "   "})

    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [1, 2, 3]


@pytest.mark.anyio
async def test_get_all_tasks_filters_description_by_query(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)
    response = await client.get("/api/v1/tasks/", params={"q": "And"})

    assert response.status_code == 200
    tasks = response.json()
    assert [task["id"] for task in tasks] == [1, 3]

    response2 = await client.get("/api/v1/tasks/", params={"q": "lOW pRi"})

    assert response2.status_code == 200
    tasks = response2.json()
    assert [task["id"] for task in tasks] == [2]


@pytest.mark.anyio
async def test_get_all_tasks_rejects_invalid_priority_query_param(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/tasks/", params={"priority": "INVALID"})

    assert response.status_code == 422
    assert response.json()["detail"]


@pytest.mark.anyio
async def test_get_all_tasks_applies_multiple_query_params_together(
    client: AsyncClient,
) -> None:
    await _seed_query_param_tasks(client)

    response = await client.get(
        "/api/v1/tasks/",
        params={
            "completed": "false",
            "priority": "HIGH",
            "due_after": "2026-02-15T00:00:00Z",
        },
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == 3
    assert tasks[0]["title"] == "Open high later"
    assert tasks[0]["completed"] is False
    assert tasks[0]["priority"] == "HIGH"


@pytest.mark.anyio
async def test_update_task_in_memory(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/tasks/", json={"title": "Initial title", "description": "Initial"}
    )

    update_response = await client.patch(
        "/api/v1/tasks/1", json={"description": "Updated"}
    )

    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert_task_shape(
        updated_task,
        expected_id=1,
        expected_title="Initial title",
        expected_description="Updated",
    )

    get_response = await client.get("/api/v1/tasks/1")

    assert get_response.status_code == 200
    fetched_task = get_response.json()
    assert fetched_task["description"] == "Updated"
    assert fetched_task["updated_at"] == updated_task["updated_at"]


@pytest.mark.anyio
async def test_complete_and_reopen_task_updates_completed_at(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/tasks/",
        json={"title": "Checklist item", "description": "toggle me"},
    )

    assert create_response.status_code == 201
    assert_task_shape(
        create_response.json(),
        expected_id=1,
        expected_title="Checklist item",
        expected_description="toggle me",
    )

    complete_response = await client.patch("/api/v1/tasks/1", json={"completed": True})

    assert complete_response.status_code == 200
    completed_task = complete_response.json()
    assert completed_task["completed"] is True
    assert completed_task["completed_at"] is not None
    assert completed_task["updated_at"] >= completed_task["created_at"]

    reopen_response = await client.patch("/api/v1/tasks/1", json={"completed": False})

    assert reopen_response.status_code == 200
    reopened_task = reopen_response.json()
    assert reopened_task["completed"] is False
    assert reopened_task["completed_at"] is None
    assert reopened_task["updated_at"] >= completed_task["updated_at"]


@pytest.mark.anyio
async def test_updating_completed_does_not_clear_existing_due_date(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/tasks/",
        json={
            "title": "Preserve due date",
            "description": "toggle completion only",
            "due_date": "2026-05-01T00:00:00Z",
        },
    )

    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["due_date"] == "2026-05-01T00:00:00Z"

    complete_response = await client.patch("/api/v1/tasks/1", json={"completed": True})

    assert complete_response.status_code == 200
    completed_task = complete_response.json()
    assert completed_task["due_date"] == "2026-05-01T00:00:00Z"

    reopen_response = await client.patch("/api/v1/tasks/1", json={"completed": False})

    assert reopen_response.status_code == 200
    reopened_task = reopen_response.json()
    assert reopened_task["due_date"] == "2026-05-01T00:00:00Z"


@pytest.mark.anyio
async def test_delete_task_in_memory(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/tasks/", json={"title": "Disposable", "description": None}
    )

    delete_response = await client.delete("/api/v1/tasks/1")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get("/api/v1/tasks/1")

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Task with id 1 not found"}


@pytest.mark.anyio
async def test_delete_all_tasks_in_memory(client: AsyncClient) -> None:
    await client.post("/api/v1/tasks/", json={"title": "First", "description": "one"})
    await client.post("/api/v1/tasks/", json={"title": "Second", "description": "two"})

    delete_response = await client.delete("/api/v1/tasks/")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    list_response = await client.get("/api/v1/tasks/")

    assert list_response.status_code == 200
    assert list_response.json() == []


@pytest.mark.anyio
async def test_get_task_returns_not_found_for_missing_id(client: AsyncClient) -> None:
    response = await client.get("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task with id 999 not found"}


@pytest.mark.anyio
async def test_update_task_returns_not_found_for_missing_id(
    client: AsyncClient,
) -> None:
    response = await client.patch("/api/v1/tasks/999", json={"title": "Missing"})

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cannot update task with id 999: task not found"
    }


@pytest.mark.anyio
async def test_delete_task_returns_not_found_for_missing_id(
    client: AsyncClient,
) -> None:
    response = await client.delete("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cannot delete task with id 999: task not found"
    }
