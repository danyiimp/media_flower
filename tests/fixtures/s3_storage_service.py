import pytest
from app.services.s3_storage_service import S3StorageService
from typing import Optional
from app.core.manifest_loader import manifests


def get_manifest_buckets(max_buckets: Optional[int] = None) -> list[str]:
    buckets = []
    for manifest in manifests.values():
        for bucket in (manifest.derived_bucket, manifest.source_bucket):
            if max_buckets is not None and len(buckets) >= max_buckets:
                return buckets
            buckets.append(bucket)
    return buckets


@pytest.fixture
def storage_service(setup_s3):
    return S3StorageService()


@pytest.fixture
async def setup_s3_buckets(storage_service):
    buckets = get_manifest_buckets(max_buckets=3)
    async with storage_service.session.client(
        "s3", endpoint_url=storage_service.endpoint_url
    ) as s3:
        for bucket in buckets:
            await s3.create_bucket(Bucket=bucket)
    return buckets
