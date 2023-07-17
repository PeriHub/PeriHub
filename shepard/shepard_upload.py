# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os
import time

from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration

from shepard_client.api.collection_api import CollectionApi
from shepard_client.models.collection import Collection

from shepard_client.api.data_object_api import DataObjectApi
from shepard_client.models.data_object import DataObject

from shepard_client.api.structureddata_api import StructureddataApi
from shepard_client.models.structured_data_container import StructuredDataContainer
from shepard_client.models.structured_data_payload import StructuredDataPayload
from shepard_client.models.structured_data import StructuredData
from shepard_client.api.structureddata_reference_api import StructureddataReferenceApi
from shepard_client.models.structured_data_reference import StructuredDataReference

from shepard_client.api.file_api import FileApi
from shepard_client.models.file_container import FileContainer

from shepard_client.api.file_reference_api import FileReferenceApi
from shepard_client.models.file_reference import FileReference


HOST = os.getenv("HOST")
APIKEY = os.getenv("APIKEY")

# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

# Create a collection
collection_api = CollectionApi(client)
collection_to_create = Collection(name="PeriHub", description="PeriHub collection")
created_collection = collection_api.create_collection(collection=collection_to_create)
print(created_collection)

# In order to upload structured data, you first need to create a container into which you can upload your data
structureddata_api = StructureddataApi(client)
container_to_create = StructuredDataContainer(name="PeriHub")
created_container = structureddata_api.create_structured_data_container(
    structured_data_container=container_to_create
)

# In order to upload a file, you first need to create a container into which you can upload your file
file_api = FileApi(client)
container_to_create = FileContainer(name="PeriHub")
file_container = file_api.create_file_container(file_container=container_to_create)

# Read local json data
models_data = []
path = "api/app/assets/models"
for model in next(os.walk(path))[1]:
    # print(model)
    with open(
        os.path.join(path, model, model + ".json"), "r", encoding="UTF-8"
    ) as file:
        response = file.read()

        ###################### Data object ######################
        # Create a data object
        dataobject_api = DataObjectApi(client)
        dataobject_to_create = DataObject(
            name=model, description=model + " data object"
        )
        created_dataobject = dataobject_api.create_data_object(
            collection_id=created_collection.id, data_object=dataobject_to_create
        )
        print(created_dataobject)

        ###################### Structured Data ######################
        # Now you can upload some data into your newly created container
        payload = StructuredDataPayload(
            structured_data=StructuredData(name=model),
            payload=response,
        )
        created_structured_data = structureddata_api.create_structured_data(
            structureddata_container_id=created_container.id,
            structured_data_payload=payload,
        )

        # You have now received an object that is the unique identifier of your uploaded data
        print(created_structured_data)

        ###################### Image file ######################
        # Now you can upload a file into your newly created container
        created_file = file_api.create_file(
            file_container_id=file_container.id,
            file=os.path.join(path, model, model + ".jpg"),
        )
        # You have now received an object that is the unique identifier of your uploaded file
        print(created_file)

        print(created_collection.id)
        print(created_dataobject.id)
        time.sleep(5)

        ###################### Reference structured Data ######################
        # With this identifier in combination with your container you can reference your data from anywhere
        structureddata_reference_api = StructureddataReferenceApi(client)
        reference_to_create = StructuredDataReference(
            name="Model data reference",
            structured_data_container_id=created_container.id,
            structured_data_oids=[created_structured_data.oid],
        )
        created_reference = (
            structureddata_reference_api.create_structured_data_reference(
                collection_id=created_collection.id,
                data_object_id=created_dataobject.id,
                structured_data_reference=reference_to_create,
            )
        )
        print(created_reference)

        ###################### Reference image files ######################
        # With this identifier in combination with your container you can reference your file from anywhere
        file_reference_api = FileReferenceApi(client)
        reference_to_create = FileReference(
            name="Model image reference",
            file_container_id=file_container.id,
            file_oids=[created_file.oid],
        )
        created_reference = file_reference_api.create_file_reference(
            collection_id=created_collection.id,
            data_object_id=created_dataobject.id,
            file_reference=reference_to_create,
        )
        print(created_reference)

        # # And now you can download your data using this newly created reference
        # structured_datas = structureddata_reference_api.get_structured_data_payload(
        #     collection_id=created_collection.id,
        #     data_object_id=created_dataobject.id,
        #     structureddata_reference_id=created_reference.id,
        # )
        # print(structured_datas)

        # # Download one specific strucutured data
        # structured_data = structureddata_reference_api.get_specific_structured_data_payload(
        #     collection_id=created_collection.id,
        #     data_object_id=created_dataobject.id,
        #     structureddata_reference_id=created_reference.id,
        #     oid=created_reference.structured_data_oids[0],
        # )

        # # Your uploaded data can be found as follows
        # print(json.loads(structured_data.payload))
