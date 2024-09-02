import pytest
from moto.server import ThreadedMotoServer
import os


@pytest.fixture
def setup_s3():
    mock_s3_server = ThreadedMotoServer(verbose=False)
    mock_s3_server.start()
    yield {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET"),
        "AWS_ENDPOINT_URL": os.getenv("AWS_ENDPOINT_URL"),
        "AWS_REGION": os.getenv("AWS_REGION"),
    }
    mock_s3_server.stop()
