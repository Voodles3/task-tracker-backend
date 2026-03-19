from pathlib import Path
from app.schemas import StorageAdapter, Task, JSONSaveData
import json

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = BASE_DIR / "save_data" / "save_data.json"


class JSONFileTaskStorage(StorageAdapter):
    def __init__(self) -> None:
        pass

    def save(self, data: JSONSaveData) -> None:
        pass

    def load(self) -> JSONSaveData:
        try:
            with (DATA_FILE_PATH).open("r", encoding="UTF-8") as f:
                raw = json.load(f)
                return JSONSaveData.model_validate(raw)

        except FileNotFoundError:
            raise FileNotFoundError("Save file not found") from None
        except json.JSONDecodeError as e:
            raise Exception("Error decoding save file JSON") from e
