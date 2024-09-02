from fastapi import FastAPI

from app.api.processing import router as processing_router
from app.api.images import router as images_router


app = FastAPI(
    title="MediaFlower API",
    description="An API for processing and managing images, including variant creation and storage management.",  # noqa
    version="1.0.0",
)

app.include_router(processing_router, prefix="/images", tags=["Create"])
app.include_router(images_router, tags=["Images"])
