import pytest
from httpx import AsyncClient
from botocore.exceptions import ClientError


from app.scripts.delete_marked_images import main as delete_marked_images
from app.services.s3_operations import storage_service
from app.schemas.image_metadata import ImageMetadataResponse
from app.models.db.image_metadata import ImageMetadataDB
from app.helpers.file_utils import get_bucket_and_key_from_s3_url


def extract_all_buckets_and_keys(
    image_metadata: ImageMetadataResponse | ImageMetadataDB,
):
    urls = [image_metadata.source.url] + [
        v.url for v in image_metadata.variants.values()
    ]
    return [get_bucket_and_key_from_s3_url(url) for url in urls]


@pytest.mark.usefixtures("setup_s3_buckets")
class TestDeleteMarkedImagesScript:
    async def test_delete_marked_images(self, ac: AsyncClient, setup_test_db):
        response = await ac.post(
            "/images/file",
            params={"project_name": "test", "image_type": "illustration"},
            files={"file": open("./tests/assets/test.png", "rb")},
        )
        assert response.status_code == 200
        response = ImageMetadataResponse(**response.json())

        buckets_keys_list = extract_all_buckets_and_keys(response)

        response = await ac.delete(f"/image/{response.id}")
        assert response.status_code == 204

        await delete_marked_images()
        for bucket, key in buckets_keys_list:
            with pytest.raises((FileNotFoundError, ClientError)):
                await storage_service.download(bucket, key)
        assert (
            await setup_test_db.images.count_documents({"deleted": True}) == 0
        )
