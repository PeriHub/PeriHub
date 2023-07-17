# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

router = APIRouter(prefix="/docs", tags=["Documentation Methods"])


@router.get("/getDocs")
def get_docs(name: str = "Introduction"):
    """doc"""

    path = name.split("_")

    if len(path) == 1:
        remotepath = "./guides/" + path[0] + ".md"
    else:
        remotepath = "./guides/" + path[0] + "/" + path[1] + ".md"

    with open(remotepath, "r", encoding="UTF-8") as file:
        response = file.read()

    return response


@router.get("/getPublications")
def get_publications():
    """doc"""

    remotepath = "./Publications/papers.bib"

    with open(remotepath, "r", encoding="UTF-8") as file:
        response = file.read()

    return response
