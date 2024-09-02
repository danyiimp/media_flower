from app.core.db_init import db
from app.models.db.image_metadata import ImageMetadataDB
from app.models.py_object_id import PyObjectId


class ImageNotFoundError(Exception):
    pass


class ImageAlreadyDeletedError(Exception):
    pass


async def save_image_metadata(metadata: ImageMetadataDB):
    await db.images.insert_one(metadata.model_dump(by_alias=True))


async def mark_image_to_delete(id_: PyObjectId):
    res = await db.images.update_one(
        {"_id": id_},
        {"$set": {"deleted": True}},
    )
    if res.matched_count == 0:
        raise ImageNotFoundError("Image not found.")
    if res.modified_count == 0:
        raise ImageAlreadyDeletedError("Image already marked as deleted.")


async def get_images_batch_to_delete(batch_size=100):
    cursor = db.images.find({"deleted": True}).limit(batch_size)
    return [ImageMetadataDB(**document) async for document in cursor]


async def get_all_images_to_delete():
    while True:
        images_batch = await get_images_batch_to_delete()
        if not images_batch:
            break
        for image in images_batch:
            yield image


async def delete_image_metadata_from_db(id_: PyObjectId):
    res = await db.images.delete_one({"_id": id_})
    if res.deleted_count == 0:
        raise ValueError("Image not found.")
