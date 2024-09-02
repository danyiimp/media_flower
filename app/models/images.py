from pydantic import BaseModel, Field
from typing import Optional


class ImageVariant(BaseModel):
    name: str
    path: str
    imgproxy_params: str
    format: Optional[str] = Field(default="webp")


class Image(BaseModel):
    name: str
    path: str
    image_variants: list[ImageVariant]
    format: Optional[str] = None
