import pytest
from app.core.db_init import client, db
import os


@pytest.fixture
async def setup_test_db():
    yield db
    print("Test MongoDB Dropped")
    await client.drop_database(os.getenv("MONGO_DB"))
