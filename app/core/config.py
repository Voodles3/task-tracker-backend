from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]


class Config(BaseSettings):
    data_file_path: Path = BASE_DIR / "data" / "tasks.json"


config = Config()
