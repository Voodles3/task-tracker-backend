from pathlib import Path
from app.schemas import StorageAdapter, Task, JSONSaveData
import json

SAVE_PATH = Path("save_data/")


class JSONFileTaskStorage(StorageAdapter):
    def __init__(self) -> None:
        self._save_file_name = "tasks.json"

    def save(self, tasks: list[Task], next_id: int) -> None:
        pass

    def load(self) -> tuple[list[Task], int]:
        try:
            with (SAVE_PATH / self._save_file_name).open("r", encoding="UTF-8") as f:
                raw = json.load(f)
                data = JSONSaveData.model_validate(raw)
                return data.tasks, data.next_id

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Save file not found: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Error decoding save file JSON: {e}")
