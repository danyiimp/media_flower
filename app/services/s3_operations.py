from typing import Optional, Union

from app.core.storage_factory import get_storage_service
from app.helpers.file_utils import content_type_from_extension
from app.models.images import Image, ImageVariant

storage_service = get_storage_service()


async def upload_to_s3(
    bucket: str,
    image: Union[Image, ImageVariant],
    key: str,
    data: bytes,
    content_type: Optional[str] = None,
):
    if content_type is None:
        content_type = content_type_from_extension(image.format)
    try:
        await storage_service.upload(bucket, key, data, content_type)
    except Exception:
        return False
    return True


async def download_image_from_s3(bucket: str, key: str) -> bytes:
    return await storage_service.download(bucket, key)


async def cleanup_s3_uploads(bucket: str, keys: list[str]):
    await storage_service.cleanup(bucket, keys)


async def delete_object_safe(bucket: str, key: str):
    await storage_service.delete(bucket, key)
