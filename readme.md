# Media Flower

**Media Flower** is a FastAPI-based image processing and management application that supports uploading, processing, and retrieving image metadata. The application uses a hybrid storage system with support for both AWS S3 and local filesystem storage, and leverages Imgproxy for image variant generation.


## Testing

To run the tests and generate coverage report, please use the following command:

```bash
pytest --cov=app --cov-report=html 