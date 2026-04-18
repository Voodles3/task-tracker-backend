class ListNotFoundError(Exception):
    def __init__(self, list_id: int) -> None:
        self.list_id = list_id
        super().__init__(f"TaskList with id {list_id} not found")


class ListHasTasksError(Exception):
    def __init__(self, list_id: int) -> None:
        self.list_id = list_id
        super().__init__(f"TaskList with id {list_id} still has tasks")


class DuplicateTaskListNameError(Exception):
    def __init__(self, list_name: str) -> None:
        self.list_name = list_name
        super().__init__(f"TaskList with name {list_name} already exists")


class StorageError(Exception):
    pass
