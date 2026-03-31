from dataclasses import dataclass

from app.store import Store


@dataclass
class AppState:
    store: Store
