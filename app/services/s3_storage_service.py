import aioboto3
import asyncio
from botocore.exceptions import ClientError

from app.core.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_ENDPOINT_URL,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
)
from app.core.abstract_storage_service import StorageService


class S3StorageService(StorageService):
    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        self.endpoint_url = AWS_ENDPOINT_URL

    async def upload(
        self, bucket: str, key: str, data: bytes, content_type: str
    ):
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            await s3.put_object(
                Bucket=bucket, Key=key, Body=data, ContentType=content_type
            )

    async def download(self, bucket: str, key: str) -> bytes:
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            response = await s3.get_object(Bucket=bucket, Key=key)
            return await response["Body"].read()

    async def delete(self, bucket: str, key: str):
        async with self.session.client(
            "s3", endpoint_url=self.endpoint_url
        ) as s3:
            try:
                await s3.delete_object(Bucket=bucket, Key=key)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "NoSuchKey":
                    print(
                        f"File {key} does not exist in bucket {bucket}, ignoring."  # noqa
                    )
                else:
                    raise

    async def cleanup(self, bucket: str, keys: list[str]):
        delete_tasks = [self.delete(bucket, key) for key in keys]
        await asyncio.gather(*delete_tasks)
