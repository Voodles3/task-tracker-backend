import os
from pathlib import Path

import pytest

from app.db.storage import JSONFileTaskStorage
from app.main import create_app
from app.models.storage import JSONSaveData, StorageError, TaskMap
from tests.helpers import create_test_client


def test_storage_save_raises_storage_error_when_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    storage = JSONFileTaskStorage(data_file_path=tmp_path / "tasks.json")
    empty_tasks: TaskMap = {}
    payload = JSONSaveData(next_id=1, tasks=empty_tasks)

    def failing_replace(src: object, dst: object) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", failing_replace)

    with pytest.raises(StorageError, match="Failed to save data"):
        storage.save(payload)


def test_storage_load_raises_storage_error_for_malformed_json(tmp_path: Path) -> None:
    file_path = tmp_path / "tasks.json"
    file_path.write_text("{not valid json", encoding="utf-8")

    storage = JSONFileTaskStorage(data_file_path=file_path)
    with pytest.raises(StorageError, match="Error decoding save file JSON"):
        storage.load()


def test_storage_uses_config_default_path_when_none_is_provided(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    default_file_path = tmp_path / "data" / "tasks.json"
    monkeypatch.setattr("app.db.storage.config.data_file_path", default_file_path)

    storage = JSONFileTaskStorage()
    empty_tasks: TaskMap = {}
    payload = JSONSaveData(next_id=1, tasks=empty_tasks)

    storage.save(payload)

    assert default_file_path.exists()


@pytest.mark.anyio
async def test_app_returns_500_on_storage_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_save(self: JSONFileTaskStorage, data: JSONSaveData) -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(JSONFileTaskStorage, "save", failing_save)

    app = create_app(data_file_path=tmp_path / "tasks.json")
    async with create_test_client(app) as client:
        response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Will fail", "description": "write failure"},
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal storage error"}


@pytest.mark.anyio
async def test_app_debug_mode_includes_storage_error_details(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_save(self: JSONFileTaskStorage, data: JSONSaveData) -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(JSONFileTaskStorage, "save", failing_save)
    app = create_app(data_file_path=tmp_path / "tasks.json")
    app.debug = True
    async with create_test_client(app) as client:
        response = await client.post(
            "/api/v1/tasks/",
            json={"title": "Will fail", "description": "write failure"},
        )

    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "Internal storage error"
    assert body["error"] == "Error creating new task"
    assert body["cause"] == "disk full"
