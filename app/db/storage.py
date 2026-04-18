import json
import os
from pathlib import Path

from app.core.config import config
from app.models.storage import (
    JSONSaveData,
    StorageAdapter,
    StorageError,
)


class JSONFileStorage(StorageAdapter):
    def __init__(self, data_file_path: Path | None = None) -> None:
        self._data_file_path = data_file_path or config.data_file_path

    def save(self, data: JSONSaveData) -> None:
        self._data_file_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._data_file_path.with_suffix(
            self._data_file_path.suffix + ".tmp"
        )

        payload = JSONSaveData.model_validate(data).model_dump(mode="json")
        try:
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._data_file_path)
        except Exception as e:
            raise StorageError("Failed to save data") from e
        finally:
            tmp_path.unlink(missing_ok=True)

    def load(self) -> JSONSaveData:
        try:
            with (self._data_file_path).open("r", encoding="utf-8") as f:
                raw = json.load(f)
                migrated = self.migrate_save_data(raw)
                return JSONSaveData.model_validate(migrated)

        except FileNotFoundError as error:
            raise FileNotFoundError("Save file not found") from error
        except json.JSONDecodeError as e:
            raise StorageError("Error decoding save file JSON") from e

    def migrate_save_data(self, raw: dict[str, object]) -> dict[str, object]:
        version = raw.get("schema_version", 1)

        if version == 1:
            return {
                "schema_version": 2,
                "next_task_id": raw["next_id"],
                "next_list_id": 1,
                "tasks": raw.get("tasks", {}),
                "lists": {},
            }
        elif version == 2:
            return raw

        raise StorageError(f"Unsupported save schema version: {version}")
