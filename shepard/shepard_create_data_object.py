# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os

from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration

from shepard_client.api.data_object_api import DataObjectApi
from shepard_client.models.data_object import DataObject


HOST = os.getenv("HOST")
APIKEY = os.getenv("APIKEY")

# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

###################### Data object ######################
# Create a data object
dataobject_api = DataObjectApi(client)
dataobject_to_create = DataObject(
    name="Test",
    description="description",
    parent_id=22115,
)
created_dataobject = dataobject_api.create_data_object(
    collection_id=13513,
    data_object=dataobject_to_create,
)
print(created_dataobject)
