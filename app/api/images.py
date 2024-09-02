from fastapi import APIRouter, HTTPException, Query, Depends, Response, status
from typing import Optional

from app.core.db_init import db
from app.models.db.image_metadata import ImageMetadataDB
from app.api.auth import authorize
from app.models.py_object_id import PyObjectId
from app.schemas.image_metadata import ImagesResponse
from app.services.db_operations import (
    mark_image_to_delete,
    ImageNotFoundError,
    ImageAlreadyDeletedError,
)

router = APIRouter()


@router.get(
    "/images",
    summary="Get Images",
    description="Retrieve a list of images with optional filtering by project name and image name.", # noqa
    response_description="A list of images with pagination details.",
)
async def get_images(
    project_name: Optional[str] = None,
    image_name: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    _: str = Depends(authorize),
):
    query = {"deleted": False}
    if project_name:
        query["project_name"] = project_name
    if image_name:
        query["image_name"] = image_name

    skip = (page - 1) * limit
    cursor = db.images.find(query).skip(skip).limit(limit)
    total_count = await db.images.count_documents(query)
    images = await cursor.to_list(length=limit)

    images = [ImageMetadataDB(**image).model_dump() for image in images]
    return ImagesResponse(
        page=page, limit=limit, total_count=total_count, images=images
    )


@router.delete(
    "/image/{id}",
    summary="Delete Image",
    description="Mark image as deleted by its ID.",
    response_description="The image has been marked as deleted.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_image(
    id: PyObjectId,
    _: str = Depends(authorize),
):
    try:
        await mark_image_to_delete(id)
    except ImageNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except ImageAlreadyDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
