from app.models.filetype_metadata import FileTypeMetadata
from app.models.manifest import Manifest
from app.models.images import Image
from typing import Tuple, List
from dataclasses import dataclass
from app.core.manifest_loader import manifests
from fastapi import HTTPException
from app.helpers.file_utils import (
    detect_file_type_metadata_from_bytes,
    detect_dims_from_bytes,
)

from app.helpers.file_utils import (
    is_mime_type_supported,
)


@dataclass
class ImageProcessingContext:
    project_name: str = None
    image_type: str = None
    src_data: bytes = None
    file_type_metadata: FileTypeMetadata = None
    manifest: Manifest = None
    src_image: Image = None
    src_extension: str = None
    src_mime_type: str = None
    src_size: Tuple[int, int] = None
    processed_variants: List[bytes] = None
    src_key: str = None
    variant_keys: List[str] = None
    variant_dims: List[Tuple[int, int]] = None
    imgproxy_service: object = None

    def __init__(self, project_name, image_type, src_data, file_type_metadata):
        super().__init__()

        self.project_name = project_name
        self.image_type = image_type
        self.src_data = src_data
        self.file_type_metadata = file_type_metadata

        self.set_manifest()
        self.set_source_image()
        self.set_source_image_metadata()

    def set_manifest(self):
        if self.project_name not in manifests:
            raise HTTPException(status_code=404, detail="Project not found")
        self.manifest = manifests[self.project_name]

    def set_source_image(self):
        try:
            src_image = next(
                image
                for image in self.manifest.images
                if image.name == self.image_type
            )
        except StopIteration as e:
            raise HTTPException(
                status_code=404, detail="Image type not found"
            ) from e  # noqa
        self.src_image = src_image

    def set_source_image_metadata(self):
        if self.file_type_metadata.is_omitted():
            src_extension, src_mime_type = (
                detect_file_type_metadata_from_bytes(self.src_data)
            )
        else:
            src_extension = self.file_type_metadata.extension
            src_mime_type = self.file_type_metadata.mime_type

        self.src_image.format = src_extension

        if is_mime_type_supported(src_mime_type):
            src_size = detect_dims_from_bytes(self.src_data)
        else:
            src_size = (None, None)

        self.src_extension = src_extension
        self.src_mime_type = src_mime_type
        self.src_size = src_size
