import os
import shutil
from typing import List

from fastapi import APIRouter, File, Request, UploadFile

from support.base_models import FileType, ResponseModel
from support.file_handler import FileHandler
from support.globals import dev, log

router = APIRouter(prefix="/upload", tags=["Upload Methods"])


@router.post("/files")
async def upload_files(
    model_name: str,
    model_folder_name: str = "Default",
    request: Request = "",
    files: List[UploadFile] = File(...),
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    localpath = FileHandler.get_local_model_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    for file in files:
        file_location = localpath + f"/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

    return ResponseModel(
        data=True,
        message=f"file '{files[0].filename}' saved at '{file_location}'",
    )


@router.put("/inputFile")
def write_input_file(
    model_name: str,
    input_string: str,
    model_folder_name: str = "Default",
    file_type: FileType = FileType.YAML,
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev[0])

    with open(
        "./Output/" + os.path.join(username, model_name, model_folder_name) + "/" + model_name + "." + file_type,
        "w",
        encoding="UTF-8",
    ) as file:
        file.write(input_string)

    log.info("%s-InputFile has been saved", model_name)
    return ResponseModel(
        data=True,
        message=model_name + "-InputFile has been saved",
    )
