from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Query, Depends
from fastapi.responses import Response

from app.models.filetype_metadata import FileTypeMetadata
from app.services.image_processing.service import handle_image_processing
from app.helpers.image_downloader import download_image
from app.services.s3_operations import download_image_from_s3
from app.api.auth import authorize
from app.helpers.make_dependable import make_dependable

router = APIRouter()


@router.post(
    "/file",
    summary="Create from Image File",
    description="Upload and process an image file, generating various image variants.",  # noqa
    response_description="The metadata of the processed image.",
)
async def process_image_file(
    project_name: str,
    image_type: str,
    file_type_metadata: Annotated[
        FileTypeMetadata, Depends(make_dependable(FileTypeMetadata))
    ],
    file: UploadFile = File(...),
    _: str = Depends(authorize),
):
    raw_bytes = await file.read()
    response = await handle_image_processing(
        project_name, image_type, raw_bytes, file_type_metadata
    )
    return Response(
        content=response.model_dump_json(), media_type="application/json"
    )


@router.post(
    "/url",
    summary="Create from Image URL",
    description="Download and process an image from a URL, generating various image variants.",  # noqa
    response_description="The metadata of the processed image.",
)
async def process_image_url(
    project_name: str,
    image_type: str,
    file_type_metadata: Annotated[
        FileTypeMetadata, Depends(make_dependable(FileTypeMetadata))
    ],
    url: str = Query(...),
    _: str = Depends(authorize),
):
    raw_bytes = await download_image(url)
    response = await handle_image_processing(
        project_name, image_type, raw_bytes, file_type_metadata
    )
    return Response(
        content=response.model_dump_json(), media_type="application/json"
    )


@router.post(
    "/s3",
    summary="Create from S3 Image",
    description="Download and process an image from S3, generating various image variants.",  # noqa
    response_description="The metadata of the processed image.",
)
async def process_image_s3(
    project_name: str,
    image_type: str,
    file_type_metadata: Annotated[
        FileTypeMetadata, Depends(make_dependable(FileTypeMetadata))
    ],
    s3_bucket: str,
    s3_key: str,
    _: str = Depends(authorize),
):
    raw_bytes = await download_image_from_s3(s3_bucket, s3_key)
    response = await handle_image_processing(
        project_name, image_type, raw_bytes, file_type_metadata
    )

    return Response(
        content=response.model_dump_json(), media_type="application/json"
    )
