import os
import aiofiles
import asyncio

from app.core.abstract_storage_service import StorageService


class LocalFilesystemStorageService(StorageService):
    def __init__(self):
        self.base_path = "local_storage"

    async def upload(
        self, bucket: str, key: str, data: bytes, content_type: str = None
    ):
        local_path = os.path.join(self.base_path, bucket, key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        async with aiofiles.open(local_path, "wb") as f:
            await f.write(data)

    async def download(self, bucket: str, key: str) -> bytes:
        local_path = os.path.join(self.base_path, bucket, key)
        async with aiofiles.open(local_path, "rb") as f:
            return await f.read()

    async def delete(self, bucket: str, key: str):
        local_path = os.path.join(self.base_path, bucket, key)
        if os.path.exists(local_path):
            # Delete file
            os.remove(local_path)

            # Delete empty directories
            dir_path = os.path.dirname(local_path)
            while dir_path != self.base_path and not os.listdir(dir_path):
                os.rmdir(dir_path)
                dir_path = os.path.dirname(dir_path)

    async def cleanup(self, bucket: str, keys: list[str]):
        delete_tasks = [self.delete(bucket, key) for key in keys]
        await asyncio.gather(*delete_tasks)
