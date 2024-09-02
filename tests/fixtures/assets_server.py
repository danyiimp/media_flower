import pytest
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

ASSETS_SERVER_PORT = 6000


class AssestsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="tests/assets", **kwargs)

    def log_message(self, format: str, *args) -> None:
        pass


class AssetsServer(HTTPServer):
    def __init__(self, port, *args, **kwargs):
        super().__init__(
            *args,
            server_address=("localhost", port),
            RequestHandlerClass=AssestsHandler,
            **kwargs
        )


@pytest.fixture(scope="module")
def setup_assets_server():
    assets_server = AssetsServer(ASSETS_SERVER_PORT)
    server_thread = Thread(target=assets_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Assets Server Startup")
    yield
    print("Assets Server Shutdown")
    assets_server.shutdown()
    server_thread.join()
