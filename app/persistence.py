import json
import os
from pathlib import Path

from app.schemas import JSONSaveData, StorageAdapter, StorageError

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = BASE_DIR / "save_data" / "save_data.json"


class JSONFileTaskStorage(StorageAdapter):
    def save(self, data: JSONSaveData) -> None:
        DATA_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = DATA_FILE_PATH.with_suffix(DATA_FILE_PATH.suffix + ".tmp")

        payload = JSONSaveData.model_validate(data).model_dump()
        try:
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, DATA_FILE_PATH)
        except Exception as e:
            raise StorageError("Failed to save data") from e
        finally:
            tmp_path.unlink(missing_ok=True)

    def load(self) -> JSONSaveData:
        try:
            with (DATA_FILE_PATH).open("r", encoding="utf-8") as f:
                raw = json.load(f)
                return JSONSaveData.model_validate(raw)

        except FileNotFoundError:
            raise FileNotFoundError("Save file not found") from None
        except json.JSONDecodeError as e:
            raise StorageError("Error decoding save file JSON") from e
