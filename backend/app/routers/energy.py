# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timedelta

import requests
from fastapi import APIRouter

from support.base_models import ResponseModel

router = APIRouter(prefix="/energy", tags=["Upload Methods"])


@router.get("/prognosis")
async def energy():
    """doc"""
    # Define the URL and query parameters
    url = "https://api.energy-charts.info/traffic_signal"
    params = {"country": "de"}

    # Send a GET request to the URL with the query parameters
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        raw_data = response.json()
        data = {}

        # Loop through the xAxisValues and data arrays
        for index, value in enumerate(raw_data[0]["data"]):
            # Convert the timestamp to a date string
            timestamp = raw_data[0]["xAxisValues"][index]
            date = datetime.utcfromtimestamp(timestamp / 1000) + timedelta(
                hours=2
            )  # Assuming the timestamp is in milliseconds and utc
            date_string = date.strftime("%Y-%m-%d %H:%M:%S")

            # Assign the value to the result dictionary with the date string as the key
            data[date_string] = value

        # Now, 'data' contains the processed data
        return ResponseModel(
            data=data,
            message="Current Energy Data retrieved successfully",
        )

    else:
        return ResponseModel(
            data=False,
            message=f"Request failed with status code {response.status_code}",
        )


@router.get("/current")
async def energy():
    """doc"""
    # Define the URL and query parameters
    url = "https://api.energy-charts.info/traffic_signal"
    params = {"country": "de"}

    # Target timestamp for which you want to find the nearest value
    target_timestamp = int(datetime.now().timestamp() * 1000)

    # Send a GET request to the URL with the query parameters
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        raw_data = response.json()

        # Find the index of the nearest timestamp in 'xAxisValues' array
        nearest_index = min(
            range(len(raw_data[0]["xAxisValues"])), key=lambda i: abs(raw_data[0]["xAxisValues"][i] - target_timestamp)
        )

        # Get the nearest value from the 'data' array
        nearest_value = raw_data[0]["data"][nearest_index]

        # Now, 'data' contains the processed data
        return ResponseModel(
            data=nearest_value,
            message="Current Energy Data retrieved successfully",
        )

    else:
        return ResponseModel(
            data=False,
            message=f"Request failed with status code {response.status_code}",
        )
