from datetime import datetime

import httpx
from fastapi import FastAPI
from httpx import AsyncClient

type TaskResponsePayload = dict[str, object]


def create_test_client(app: FastAPI) -> AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return AsyncClient(
        transport=transport,
        base_url="http://testserver",
    )


def assert_task_shape(
    task: TaskResponsePayload,
    *,
    expected_id: int,
    expected_title: str,
    expected_description: str | None,
    expected_priority: str = "UNSET",
    expected_completed: bool = False,
    expected_due_date: str | None = None,
    expected_completed_at: str | None = None,
) -> None:
    assert task["id"] == expected_id
    assert task["title"] == expected_title
    assert task["description"] == expected_description
    assert task["priority"] == expected_priority
    assert task["completed"] is expected_completed
    assert task["due_date"] == expected_due_date
    assert task["completed_at"] == expected_completed_at

    created_at = task["created_at"]
    updated_at = task["updated_at"]

    assert isinstance(created_at, str)
    assert isinstance(updated_at, str)
    assert datetime.fromisoformat(created_at).tzinfo is not None
    assert datetime.fromisoformat(updated_at).tzinfo is not None
