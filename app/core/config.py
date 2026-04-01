from pathlib import Path

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    data_file_path: Path = Path("app/save_data/tasks.json")


config = Config()
