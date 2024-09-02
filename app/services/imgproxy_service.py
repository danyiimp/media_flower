import aiohttp
import asyncio
import os
from fastapi import HTTPException
from uuid import uuid4

from app.core.settings import IMGPROXY_FILESYSTEM_FOLDER, IMGPROXY_URL
from app.models.images import ImageVariant, Image


class ImgproxyService:
    def __init__(self, image: Image, image_data: bytes):
        self.image = image
        self.image_data = image_data
        self.imgproxy_folder = IMGPROXY_FILESYSTEM_FOLDER
        self.imgproxy_path = self._generate_unique_filename("image")
        self.full_imgproxy_path = os.path.join(
            self.imgproxy_folder, self.imgproxy_path
        )

    def _imgproxy_url(self, variant: ImageVariant):
        path = f"local:///{self.imgproxy_path}@{variant.format}"
        return f"{IMGPROXY_URL}/insecure/{variant.imgproxy_params}/plain/{path}"  # noqa

    def _generate_unique_filename(self, filename):
        unique_id = uuid4()
        unique_filename = f"{unique_id}_{filename}"
        return unique_filename

    async def create_variants(self):
        try:
            results = await asyncio.gather(
                *[
                    self._create_variant(variant)
                    for variant in self.image.image_variants
                ]
            )
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await self.cleanup()

    async def _create_variant(self, variant: ImageVariant):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._imgproxy_url(variant)) as response:
                response.raise_for_status()
                variant_data = await response.read()
                return variant_data

    async def save_image_to_filesystem(self, data: bytes):
        with open(self.full_imgproxy_path, "wb") as file:
            file.write(data)

    async def cleanup(self):
        if os.path.exists(self.full_imgproxy_path):
            os.remove(self.full_imgproxy_path)
