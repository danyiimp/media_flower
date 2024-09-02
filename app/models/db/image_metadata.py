from pydantic import BaseModel
from typing import Optional
from pydantic import Field

from app.models.py_object_id import PyObjectId


class AssetDB(BaseModel):
    url: str
    width: Optional[int]
    height: Optional[int]
    size: int
    format: str


class ImageMetadataDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    version: int
    project_name: str
    image_name: str
    source: AssetDB
    variants: dict[str, AssetDB]
    deleted: bool = False
