# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from typing import List

import magic
from fastapi import APIRouter, File, Request, UploadFile

from ..support.base_models import ResponseModel
from ..support.file_handler import FileHandler
from ..support.globals import dev, log

router = APIRouter(prefix="/upload", tags=["Upload Methods"])


@router.post("/files")
async def upload_files(
    model_name: str,
    model_folder_name: str = "Default",
    request: Request = "",
    files: List[UploadFile] = File(...),
):
    """doc"""

    # Check file size
    for file in files:
        if file.size > 2 * 1024 * 1024:  # 2 MB
            # more than 2 MB
            return ResponseModel(
                data=False,
                message=f"File too large, max file size is 2 MB, got {file.size} bytes",
            )

    # Initialize magic library
    mime = magic.Magic(mime=True)

    # check the content type (MIME type)
    allowed_types = ["application/json", ".yaml", ".cdb", ".inp", ".gcode", ".obj", "text/plain", ".g", ".so", ".inp"]
    for file in files:
        content_type = mime.from_buffer(file.file.read(1024))  # Check only the first 1024 bytes
        # move the cursor back to the beginning
        await file.seek(0)
        if content_type not in allowed_types:
            log.warning("Invalid file type, got %s, expected %s", content_type, allowed_types)
            return ResponseModel(
                data=False,
                message=f"Invalid file type, got {content_type}, expected 'application/json', '.yaml', '.cdb', '.inp', '.gcode', '.obj', 'text/plain', '.g', '.so' or '.inp'",
            )

    username = FileHandler.get_user_name(request, dev)

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
    request: Request = "",
):
    """doc"""
    username = FileHandler.get_user_name(request, dev)

    with open(
        "./simulations/" + os.path.join(username, model_name, model_folder_name) + "/" + model_name + ".yaml",
        "w",
        encoding="UTF-8",
    ) as file:
        file.write(input_string)

    log.info("%s-InputFile has been saved", model_name)
    return ResponseModel(
        data=True,
        message=model_name + "-InputFile has been saved",
    )
