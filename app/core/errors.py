class ListNotFoundError(Exception):
    def __init__(self, list_id: int) -> None:
        self.list_id = list_id
        super().__init__(f"TaskList with id {list_id} not found")


class ListHasTasksError(Exception):
    def __init__(self, list_id: int) -> None:
        self.list_id = list_id
        super().__init__(f"TaskList with id {list_id} still has tasks")


class StorageError(Exception):
    pass
