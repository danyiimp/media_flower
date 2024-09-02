import os


AVAILABLE_MIME_TYPE_EXTENSION_MAP = {
    "image/svg+xml": ("svg",),
    "image/png": ("png",),
    "image/jpeg": ("jpeg", "jpg"),
    "image/webp": ("webp",),
}

IMGPROXY_FILESYSTEM_FOLDER = os.getenv(
    "IMGPROXY_FILESYSTEM_FOLDER",
    "imgproxy/filesystem",
)

IMGPROXY_URL = os.getenv(
    "IMGPROXY_URL",
    "http://localhost:8080",
)


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "media_flower")

USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "password")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")  # noqa
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", None)

APP_ENV = os.getenv("APP_ENV", "development").lower()
