# flake8: noqa: E402
import asyncio

import pytest
from httpx import AsyncClient, ASGITransport, BasicAuth
from app.core.settings import USERNAME, PASSWORD
from app import app

pytest_plugins = [
    "tests.fixtures.s3_moto_server",
    "tests.fixtures.s3_storage_service",
    "tests.fixtures.db",
    "tests.fixtures.assets_server",
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def ac():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        auth=BasicAuth(USERNAME, PASSWORD),
    ) as ac:
        print("Async Client Created")
        yield ac
        print("Async Client Deleted")
