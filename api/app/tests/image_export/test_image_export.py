import os
import shutil

from app.api_main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_result_image_from_exodus():
    test_path = "./tests/image_export/"
    file_name = "Dogbone_Output1.e"
    remote_path = "./Results/dev/Dogbone/Default"

    os.makedirs(remote_path, exist_ok=True)
    shutil.copy(
        os.path.join(test_path, file_name),
        os.path.join(remote_path, file_name),
    )

    response = client.get("/getImagePython")
    assert response.status_code == 200
    shutil.rmtree("./Results")
