# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

router = APIRouter(tags=["Documentation Methods"])


@router.get("/publications", operation_id="get_publications")
def get_publications() -> str:
    """PeriHub/PeriLab publications as BibTeX (`Publications/papers.bib`)."""

    remotepath = "./Publications/papers.bib"

    with open(remotepath, "r", encoding="UTF-8") as file:
        response = file.read()

    return response
