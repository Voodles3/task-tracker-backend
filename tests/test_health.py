import pytest


@pytest.mark.anyio
async def test_health_endpoint_returns_ok(client):
    response = await client.get("/api/v1/tasks/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
