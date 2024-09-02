import pytest
from httpx import AsyncClient


@pytest.fixture
async def create_image_in_s3_bucket(storage_service):
    with open("tests/assets/test.png", "rb") as file:
        async with storage_service.session.client(
            "s3", endpoint_url=storage_service.endpoint_url
        ) as s3:
            await s3.create_bucket(Bucket="test_bucket")
            await s3.put_object(
                Bucket="test_bucket", Key="test_image.png", Body=file
            )
    return ("test_bucket", "test_image.png")


@pytest.mark.usefixtures("setup_test_db", "setup_s3_buckets")
class TestFromS3Image:
    async def test_create_from_s3_image(
        self, ac: AsyncClient, create_image_in_s3_bucket
    ):
        bucket, key = create_image_in_s3_bucket
        response = await ac.post(
            "/images/s3",
            params={
                "project_name": "test",
                "image_type": "illustration",
                "s3_bucket": bucket,
                "s3_key": key,
            },
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data.get("project_name") == "test"
        assert response_data.get("image_name") == "illustration"
