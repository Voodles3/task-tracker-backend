import httpx
from fastapi import FastAPI
from httpx import AsyncClient


def create_test_client(app: FastAPI) -> AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return AsyncClient(
        transport=transport,
        base_url="http://testserver",
    )
