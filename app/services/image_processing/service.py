import asyncio
from fastapi import HTTPException
from app.services.image_processing.context import (
    ImageProcessingContext,
)

from app.schemas.image_metadata import ImageMetadataResponse
from app.services.imgproxy_service import ImgproxyService
from app.services.s3_operations import (
    upload_to_s3,
    cleanup_s3_uploads,
    delete_object_safe,
)
from app.services.db_operations import save_image_metadata
from app.models.db.image_metadata import ImageMetadataDB, AssetDB
from app.models.images import ImageVariant
from app.models.filetype_metadata import FileTypeMetadata
from app.helpers.file_utils import (
    generate_s3_key,
    is_mime_type_supported,
)
from app.helpers.file_utils import (
    detect_file_type_metadata_from_bytes,
    detect_dims_from_bytes,
)


async def handle_image_processing(
    project_name: str,
    image_type: str,
    src_data: bytes,
    file_type_metadata: FileTypeMetadata,
):

    context = ImageProcessingContext(
        project_name, image_type, src_data, file_type_metadata
    )

    await generate_image_variants(context)

    await upload_images(context)

    metadata = await generate_image_metadata(context)

    return ImageMetadataResponse(**metadata.model_dump())


async def generate_image_variants(c: ImageProcessingContext):
    imgproxy_service = ImgproxyService(c.src_image, c.src_image)

    await imgproxy_service.save_image_to_filesystem(c.src_data)
    processed_variants = await imgproxy_service.create_variants()
    c.imgproxy_service = imgproxy_service
    c.processed_variants = processed_variants


async def upload_images(c: ImageProcessingContext):

    c.src_key = generate_s3_key(c.src_image)
    c.variant_keys = [
        generate_s3_key(variant, c.src_image.path)
        for variant in c.src_image.image_variants
    ]

    try:
        is_ok = await upload_to_s3(
            c.manifest.source_bucket,
            c.src_image,
            c.src_key,
            c.src_data,
            c.src_mime_type,
        )

        if not is_ok:
            raise HTTPException(
                status_code=500, detail="Error uploading source image"
            )

        await upload_variants_to_s3(
            c.manifest.derived_bucket,
            c.src_image.image_variants,
            c.variant_keys,
            c.processed_variants,
        )

    except Exception as e:
        # Cleanup source image from S3
        await delete_object_safe(c.manifest.source_bucket, c.src_key)

        # Cleanup S3 uploads
        await cleanup_s3_uploads(c.manifest.derived_bucket, c.variant_keys)
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        # Ensure filesystem cleanup
        await c.imgproxy_service.cleanup()

    c.variant_dims = [
        detect_dims_from_bytes(data) for data in c.processed_variants
    ]


async def generate_image_metadata(c: ImageProcessingContext):
    metadata = ImageMetadataDB(
        version=c.manifest.version,
        project_name=c.project_name,
        image_name=c.image_type,
        source=AssetDB(
            url=f"s3://{c.manifest.source_bucket}/{c.src_key}",
            width=c.src_size[0],
            height=c.src_size[1],
            size=len(c.src_data),
            format=c.src_extension,
        ),
        variants={
            variant.name: AssetDB(
                url=f"s3://{c.manifest.derived_bucket}/{key}",
                width=dims[0],
                height=dims[1],
                size=len(data),
                format=variant.format,
            )
            for variant, key, data, dims in zip(
                c.src_image.image_variants,
                c.variant_keys,
                c.processed_variants,
                c.variant_dims,
            )
        },
    )
    await save_image_metadata(metadata)
    return metadata


def get_source_image_metadata(src_data, file_type_metadata, src_image):
    if file_type_metadata.is_omitted():
        src_extension, src_mime_type = detect_file_type_metadata_from_bytes(
            src_data
        )
    else:
        src_extension = file_type_metadata.extension
        src_mime_type = file_type_metadata.mime_type

    src_image.format = src_extension

    if is_mime_type_supported(src_mime_type):
        src_size = detect_dims_from_bytes(src_data)
    else:
        src_size = (None, None)
    return src_extension, src_mime_type, src_size


def get_source_image(image_type, project_manifest):
    try:
        src_image = next(
            image
            for image in project_manifest.images
            if image.name == image_type
        )
    except StopIteration as e:
        raise HTTPException(
            status_code=404, detail="Image type not found"
        ) from e  # noqa
    return src_image


async def upload_variants_to_s3(
    bucket: str,
    images: list[ImageVariant],
    keys: list[str],
    data_list: list[bytes],
):
    upload_tasks = [
        upload_to_s3(bucket, image, key, data)
        for image, key, data in zip(images, keys, data_list)
    ]
    return await asyncio.gather(*upload_tasks)
