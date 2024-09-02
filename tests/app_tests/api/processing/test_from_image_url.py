import pytest
from httpx import AsyncClient
from tests.fixtures.assets_server import ASSETS_SERVER_PORT


@pytest.mark.usefixtures(
    "setup_s3_buckets", "setup_test_db", "setup_assets_server"
)
class TestProcessingFromImageURL:
    async def test_create_from_image_url(self, ac: AsyncClient):
        response = await ac.post(
            "/images/url",
            params={
                "project_name": "test",
                "image_type": "illustration",
                "url": f"http://localhost:{ASSETS_SERVER_PORT}/test.png",
            },
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data.get("project_name") == "test"
        assert response_data.get("image_name") == "illustration"
