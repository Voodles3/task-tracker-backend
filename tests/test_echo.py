import pytest


@pytest.mark.anyio
async def test_root_endpoint_returns_expected_payload(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"You are at root": True}
