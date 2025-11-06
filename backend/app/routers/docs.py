# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

router = APIRouter(prefix="/docs", tags=["Documentation Methods"])


@router.get("/getPublications", operation_id="get_publications")
def get_publications() -> str:
    """doc"""

    remotepath = "./Publications/papers.bib"

    with open(remotepath, "r", encoding="UTF-8") as file:
        response = file.read()

    return response
