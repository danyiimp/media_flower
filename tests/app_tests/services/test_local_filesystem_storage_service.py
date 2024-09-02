import os
import pytest
import shutil

from app.services.local_filesystem_storage_service import (
    LocalFilesystemStorageService,
)


@pytest.fixture
def local_storage_service(tmp_path):
    service = LocalFilesystemStorageService()
    service.base_path = tmp_path / "local_storage"
    yield service
    if service.base_path.exists():
        shutil.rmtree(service.base_path)


@pytest.fixture
def test_data():
    return {
        "bucket": "test_bucket",
        "key": "test_file.txt",
        "data": b"Hello, world!",
    }


def local_path(service, bucket, key):
    return os.path.join(service.base_path, bucket, key)


async def upload_file(service, bucket, key, data):
    await service.upload(bucket, key, data)


@pytest.mark.asyncio
async def test_upload(local_storage_service, test_data):
    bucket = test_data["bucket"]
    key = test_data["key"]
    data = test_data["data"]

    await upload_file(local_storage_service, bucket, key, data)

    path = local_path(local_storage_service, bucket, key)
    assert os.path.exists(path), "File was not created"
    with open(path, "rb") as f:
        assert f.read() == data, "File content does not match"


@pytest.mark.asyncio
async def test_download(local_storage_service, test_data):
    bucket = test_data["bucket"]
    key = test_data["key"]
    data = test_data["data"]

    await upload_file(local_storage_service, bucket, key, data)

    downloaded_data = await local_storage_service.download(bucket, key)

    assert (
        downloaded_data == data
    ), "Downloaded data does not match uploaded data"


@pytest.mark.asyncio
async def test_delete(local_storage_service, test_data):
    bucket = test_data["bucket"]
    key = test_data["key"]
    data = test_data["data"]

    await upload_file(local_storage_service, bucket, key, data)

    await local_storage_service.delete(bucket, key)

    path = local_path(local_storage_service, bucket, key)
    assert not os.path.exists(path), "File was not deleted"

    assert not os.path.exists(
        os.path.dirname(path)
    ), "Directory was not deleted"


@pytest.mark.asyncio
async def test_cleanup(local_storage_service, test_data):
    bucket = test_data["bucket"]
    data = test_data["data"]
    keys = ["file1.txt", "file2.txt", "file3.txt"]

    for key in keys:
        await upload_file(local_storage_service, bucket, key, data)

    await local_storage_service.cleanup(bucket, keys)

    for key in keys:
        path = local_path(local_storage_service, bucket, key)
        assert not os.path.exists(path), f"{key} was not deleted"

    assert not os.path.exists(
        os.path.join(local_storage_service.base_path, bucket)
    ), "Bucket directory was not deleted"
