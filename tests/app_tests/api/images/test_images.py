import pytest
from httpx import AsyncClient


async def create_image(ac: AsyncClient):
    response = await ac.post(
        "/images/file",
        params={"project_name": "test", "image_type": "illustration"},
        files={"file": open("tests/assets/test.png", "rb")},
    )
    return response.json()


@pytest.fixture
async def test_image(ac: AsyncClient):
    return await create_image(ac)


@pytest.mark.usefixtures(
    "setup_s3_buckets",
    "setup_test_db"
)
class TestImages:
    async def test_get_images(self, ac: AsyncClient):
        for _ in range(3):
            await create_image(ac)
        response = await ac.get("/images")
        assert response.status_code == 200
        response = response.json()
        assert response["total_count"] == 3

    async def test_delete_image(self, ac: AsyncClient, test_image):
        response = await ac.delete(f"/image/{test_image['id']}")
        assert response.status_code == 204

    async def test_delete_twice_and_non_existent(
        self, ac: AsyncClient, test_image
    ):
        response = await ac.delete(f"/image/{test_image['id']}")
        response = await ac.delete(f"/image/{test_image['id']}")
        assert response.status_code == 400
