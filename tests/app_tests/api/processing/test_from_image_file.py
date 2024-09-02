import pytest
from httpx import AsyncClient


async def make_request(
    ac: AsyncClient,
    image_type: str,
    extension: str = None,
    mimetype: str = None,
):
    params = {"project_name": "test", "image_type": image_type}

    if mimetype:
        params["mime_type"] = mimetype
    if extension:
        params["extension"] = extension

    response = await ac.post(
        "/images/file",
        params=params,
        files={"file": open("tests/assets/test.png", "rb")},
    )
    return response


@pytest.mark.usefixtures(
    "setup_s3_buckets", "setup_test_db"
)
class TestProcessingFromImageFile:
    @pytest.mark.parametrize(
        "image_type, expected_variants_exist",
        [
            ("illustration", True),
            ("some_image", False),
        ],
    )
    async def test_create_from_image_file(
        self,
        ac: AsyncClient,
        image_type: str,
        expected_variants_exist: bool,
    ):
        response = await make_request(ac, image_type)

        assert response.status_code == 200

        response_data = response.json()

        assert response_data.get("project_name") == "test"
        assert response_data.get("image_name") == image_type

        for dim in ["width", "height"]:
            assert isinstance(response_data.get("source", {}).get(dim), int)

        if expected_variants_exist:
            assert "variants" in response_data and response_data["variants"]
        else:
            assert not response_data.get("variants")

    @pytest.mark.parametrize(
        "extension, mimetype",
        [
            ("jpg", None),
            (None, "image/jpeg"),
        ],
    )
    async def test_create_from_image_file_with_incorrect_metadata_params(
        self, ac: AsyncClient, extension: str, mimetype: str
    ):
        response = await make_request(ac, "illustration", extension, mimetype)

        assert response.status_code == 422

    @pytest.mark.parametrize(
        "extension, mimetype",
        [
            ("3d", "model/3d"),
            ("jpg", "image/jpeg"),
        ],
    )
    async def test_create_from_image_file_with_custom_metadata(
        self, ac: AsyncClient, extension: str, mimetype: str
    ):
        response = await make_request(ac, "illustration", extension, mimetype)
        assert response.status_code == 200
