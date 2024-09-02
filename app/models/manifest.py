from pydantic import BaseModel

from app.models.images import Image


class Manifest(BaseModel):
    version: int
    name: str
    source_bucket: str
    derived_bucket: str
    images: list[Image]
