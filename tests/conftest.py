import httpx
import pytest

from app.main import app, store


@pytest.fixture(autouse=True)
def reset_store():
    store._tasks.clear()
    store._next_id = 1
    yield
    store._tasks.clear()
    store._next_id = 1


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client
