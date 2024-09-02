import random
import re
from nanoid import generate
import string
from typing import Optional, Union
import filetype
from PIL import Image as PillowImage
from io import BytesIO
import xml.etree.ElementTree as ET

from app.core.settings import AVAILABLE_MIME_TYPE_EXTENSION_MAP
from app.models.images import Image, ImageVariant


def generate_random_folder_name():
    return "".join(random.choice(string.ascii_lowercase) for _ in range(2))


def generate_unique_nanoid(size=16):
    return generate(size=size)


def generate_s3_key(
    image: Union[Image, ImageVariant], src_path: Optional[str] = None
):
    if not image.format:
        raise ValueError("Cannot generate S3 key without image format")
    sharding_path = generate_random_folder_name()
    nano_id = generate_unique_nanoid()
    if src_path:
        return (
            f"{sharding_path}/{src_path}/{image.path}/{nano_id}.{image.format}"
        )
    return f"{sharding_path}/{image.path}/{nano_id}.{image.format}"


def get_bucket_and_key_from_s3_url(url: str) -> tuple[str, str]:
    pattern = r"s3://([^/]+)/(.+)"
    match = re.match(pattern, url)
    if match:
        bucket, key = match.groups()
        return bucket, key
    raise ValueError("Invalid S3 URL")


def is_mime_type_supported(mime_type: Optional[str]) -> bool:
    return mime_type in AVAILABLE_MIME_TYPE_EXTENSION_MAP.keys()


def detect_file_type_metadata_from_bytes(byte_data):
    if is_svg(byte_data):
        return "svg"
    fileinfo = filetype.guess(byte_data)
    if fileinfo is None:
        raise ValueError("Cannot determine file type")

    return fileinfo.extension, fileinfo.mime


def detect_dims_from_bytes(byte_data):
    if is_svg(byte_data):
        return svg_dims(byte_data)

    with PillowImage.open(BytesIO(byte_data)) as image:
        return image.size


def is_svg(byte_data):
    return "<svg" in str(byte_data[0:100])


def svg_dims(byte_data):

    try:
        svg_string = byte_data.decode("utf-8")
        root = ET.fromstring(svg_string)

        width = root.attrib.get("width")
        height = root.attrib.get("height")

        width = int(round(float(width))) if width is not None else None
        height = int(round(float(height))) if height is not None else None

        return width, height
    except (ET.ParseError, ValueError) as e:
        # Handle parsing errors or invalid float conversion
        raise ValueError("Invalid SVG byte data or attributes.") from e


def content_type_from_extension(extension):
    if extension == "svg":
        return "image/svg+xml"
    return f"image/{extension}"
