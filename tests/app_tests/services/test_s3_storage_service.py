import pytest


@pytest.mark.asyncio
async def test_upload(storage_service, setup_s3_buckets):
    for bucket in setup_s3_buckets:
        await storage_service.upload(bucket, "key", b"bytes", "bytes")

    # Verify upload by downloading the file
    for bucket in setup_s3_buckets:
        downloaded_data = await storage_service.download(bucket, "key")
        assert downloaded_data == b"bytes", "Uploaded data does not match"


@pytest.mark.asyncio
async def test_download(storage_service, setup_s3_buckets):
    for bucket in setup_s3_buckets:
        data = await storage_service.download(bucket, "key")
        assert data == b"bytes", "Downloaded data does not match uploaded data"


@pytest.mark.asyncio
async def test_delete(storage_service, setup_s3_buckets):
    for bucket in setup_s3_buckets:
        await storage_service.delete(bucket, "key")

    # Verify that deletion is successful
    for bucket in setup_s3_buckets:
        with pytest.raises(Exception):
            await storage_service.download(bucket, "key")


@pytest.mark.asyncio
async def test_deleted(storage_service, setup_s3_buckets):
    for bucket in setup_s3_buckets:
        with pytest.raises(Exception):
            await storage_service.download(bucket, "key")
