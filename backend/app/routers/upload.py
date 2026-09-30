# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
from typing import List

import magic
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

# from ..support.base_models import
from ..support.file_handler import FileHandler
from ..support.globals import log, trial

router = APIRouter(prefix="/workspaces", tags=["Upload Methods"])


@router.post("/{model_name}/{model_folder_name}/files", operation_id="upload_files")
async def upload_files(
    model_name: str,
    model_folder_name: str = "Default",
    request: Request = "",
    files: List[UploadFile] = File(...),
) -> str:
    """Upload files (mesh, input deck, material, ...) into a model folder, checked by MIME type; 2 MB per file in
    trial mode. Returns the name of an uploaded `.txt` point mesh (recognized by its `header: x y` line), or "" if
    there is none."""

    # Check file size
    if trial:
        for file in files:
            if file.size > 2 * 1024 * 1024:  # 2 MB
                # more than 2 MB
                log.info(f"File too large, max file size is 2 MB, got {file.size} bytes")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"File too large, max file size is 2 MB, got {file.size} bytes",
                )

    # Initialize magic library
    mime = magic.Magic(mime=True)

    # check the content type (MIME type)
    allowed_types = [
        "application/json",
        ".yaml",
        ".cdb",
        ".inp",
        ".gcode",
        "application/x-netcdf",
        ".obj",
        "text/plain",
        ".g",
        "application/octet-stream",  # exodus files
        ".so",
        ".inp",
    ]
    for file in files:
        content_type = mime.from_buffer(file.file.read(1024))  # Check only the first 1024 bytes
        # move the cursor back to the beginning
        await file.seek(0)
        if content_type not in allowed_types:
            log.warning("Invalid file type, got %s, expected %s", content_type, allowed_types)
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                message=f"Invalid file type, got {content_type}, expected 'application/json', '.yaml', '.cdb', '.inp', '.gcode', 'application/x-netcdf', '.obj', 'text/plain', '.g', 'application/octet-stream', '.so' or '.inp'",
            )

    username = FileHandler.get_user_name(request)

    localpath = FileHandler.get_local_model_folder_path(username, model_name, model_folder_name)

    if not os.path.exists(localpath):
        os.makedirs(localpath)

    meshfile_name = ""
    for file in files:
        file_location = localpath + f"/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        if file.filename.endswith(".txt"):
            line_id = 0
            # check if file contains header
            with open(file_location) as f:
                for line in f:
                    line_id += 1
                    if line_id == 10:
                        break
                    if line.startswith("header: x y "):
                        meshfile_name = file.filename
                        break

    return meshfile_name


@router.put("/{model_name}/{model_folder_name}/input-deck", operation_id="write_input_file")
def write_input_file(
    model_name: str,
    input_string: str,
    model_folder_name: str = "Default",
    request: Request = "",
):
    """Overwrite the model folder's input deck (`<model>.yaml`) with `input_string`, e.g. after editing it in the
    text view."""
    username = FileHandler.get_user_name(request)

    with open(
        FileHandler.get_local_model_folder_path(username, model_name, model_folder_name) + "/" + model_name + ".yaml",
        "w",
        encoding="UTF-8",
    ) as file:
        file.write(input_string)

    log.info("%s-InputFile has been saved", model_name)
