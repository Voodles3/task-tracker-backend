from logging import getLogger
from threading import Lock

from app.models.storage import JSONSaveData, StorageAdapter

logger = getLogger(__name__)


class RepositoryContext:
    def __init__(self, storage: StorageAdapter) -> None:
        self._storage = storage
        self._lock = Lock()

        try:
            self.state = storage.load()
        except FileNotFoundError:
            self.state = JSONSaveData(
                next_task_id=1, next_list_id=1, tasks={}, lists={}
            )
            logger.info("No save data to load, starting fresh!")

    @property
    def lock(self) -> Lock:
        return self._lock

    def save(self) -> None:
        self._storage.save(self.state)
