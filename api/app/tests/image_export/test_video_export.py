import os
import shutil

from fastapi.testclient import TestClient

from app.api_main import app

client = TestClient(app)


def test_get_gif():
    dev = os.environ.get("DEV")
    test_path = "./tests/image_export/"
    file_name = "Dogbone_Output1.e"
    if dev:
        remote_path = "./Results/dev/Dogbone/Default"
    else:
        remote_path = "./Results/guest/Dogbone/Default"

    os.makedirs(remote_path, exist_ok=True)
    shutil.copy(
        os.path.join(test_path, file_name),
        os.path.join(remote_path, file_name),
    )

    response = client.get("/getGif")
    assert response.status_code == 200
    shutil.rmtree("./Results")
