from typing import Optional
from pydantic import BaseModel

from app.models.py_object_id import PyObjectId


class AssetResponse(BaseModel):
    url: str
    width: Optional[int]
    height: Optional[int]
    size: int
    format: str


class ImageMetadataResponse(BaseModel):
    id: PyObjectId
    version: int
    project_name: str
    image_name: str
    source: AssetResponse
    variants: dict[str, AssetResponse]


class ImagesResponse(BaseModel):
    page: int
    limit: int
    total_count: int
    images: list[ImageMetadataResponse]
