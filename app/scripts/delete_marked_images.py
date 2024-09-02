import asyncio

from app.helpers.file_utils import get_bucket_and_key_from_s3_url
from app.models.db.image_metadata import ImageMetadataDB
from app.services.db_operations import (
    get_all_images_to_delete,
    delete_image_metadata_from_db,
)
from app.services.s3_operations import delete_object_safe


async def delete_src_image_and_variants_from_s3(
    image: ImageMetadataDB,
) -> tuple[int, int]:
    src_deleted = False
    deleted_variants = 0
    try:

        # Delete source image
        bucket, key = get_bucket_and_key_from_s3_url(image.source.url)
        await delete_object_safe(bucket, key)
        src_deleted = True

        # Delete variants
        for variant in image.variants.values():
            bucket, key = get_bucket_and_key_from_s3_url(variant.url)
            await delete_object_safe(bucket, key)
            deleted_variants += 1
    except Exception as e:
        if not src_deleted:
            print(
                f"Error deleting image and its variants: {image.source.url}: {e}" # noqa
            )
            return 0, 0
        if deleted_variants < len(image.variants.values()):
            print(
                f"Error deleting {len(image.variants.values()) - deleted_variants}" # noqa
                f" variants for image {image.source.url}: {e}"
            )
            return 1, deleted_variants

    return int(src_deleted), deleted_variants


async def main():
    total_src_deleted = 0
    total_variants_deleted = 0

    async for image in get_all_images_to_delete():
        src_deleted, variants_deleted = (
            await delete_src_image_and_variants_from_s3(image)
        )
        total_src_deleted += src_deleted
        total_variants_deleted += variants_deleted
        await delete_image_metadata_from_db(image.id)
    print(
        f"Deleted {total_src_deleted} source images and {total_variants_deleted} variants." # noqa
    )
    return total_src_deleted, total_variants_deleted


if __name__ == "__main__":
    asyncio.run(main())
