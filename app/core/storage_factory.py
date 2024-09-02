from app.core.settings import APP_ENV
from app.services.s3_storage_service import S3StorageService
from app.services.local_filesystem_storage_service import (
    LocalFilesystemStorageService,
)


def get_storage_service():
    if APP_ENV == "development":
        return LocalFilesystemStorageService()
    return S3StorageService()
