import pytest
from httpx import AsyncClient

from app.core.manifest_loader import load_all_manifests
from app.schemas.image_metadata import ImagesResponse
from app.scripts.sync_manifests import main as sync_manifests
from app.helpers.file_utils import get_bucket_and_key_from_s3_url
from app.services.s3_operations import storage_service


@pytest.mark.usefixtures("setup_test_db", "setup_s3_buckets")
class TestSyncManifestsScript:

    async def test_sync_manifests(self, ac: AsyncClient):
        # Prepare some images
        response = await ac.post(
            "/images/file",
            params={"project_name": "test", "image_type": "illustration"},
            files={"file": open("tests/assets/test.png", "rb")},
        )
        assert response.status_code == 200
        response = await ac.post(
            "/images/file",
            params={"project_name": "test", "image_type": "some_image"},
            files={"file": open("tests/assets/test.png", "rb")},
        )
        assert response.status_code == 200

        all_manifests = load_all_manifests(
            ["./manifests", "./tests/assets/manifests"]
        )
        response = await ac.get("/images")
        response = response.json()
        for image_metadata in response["images"]:
            bucket, key = get_bucket_and_key_from_s3_url(
                image_metadata["source"]["url"]
            )
            await storage_service.download(bucket, key)

        await sync_manifests(all_manifests)
        response = await ac.get("/images")

        assert response.status_code == 200
        response = ImagesResponse(**response.json())
        for image_metadata in response.images:
            assert image_metadata.version == 2
