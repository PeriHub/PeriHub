import os

from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration

from shepard_client.api.structureddata_api import StructureddataApi
from shepard_client.models.structured_data_payload import StructuredDataPayload
from shepard_client.models.structured_data import StructuredData
from shepard_client.api.structureddata_reference_api import StructureddataReferenceApi
from shepard_client.models.structured_data_reference import StructuredDataReference

HOST = os.getenv("HOST")
APIKEY = os.getenv("APIKEY")

# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

# In order to upload structured data, you first need to create a container into which you can upload your data
structureddata_api = StructureddataApi(client)

collection_id = 22058
# dataobject_id = 12196
dataobject_id = 22064
container_id = 22060

# Read local json data
model = "CompactTension"
# model = "Smetana"
path = "api/app/assets/models"
# for model in next(os.walk(path))[1]:

with open(
    os.path.join(path, model, model + "Props.json"), "r", encoding="UTF-8"
) as file:
    response = file.read()

    ###################### Structured Data ######################
    # Now you can upload some data into your newly created container
    payload = StructuredDataPayload(
        structured_data=StructuredData(name=model + "Props"),
        payload=response,
    )
    created_structured_data = structureddata_api.create_structured_data(
        structureddata_container_id=container_id, structured_data_payload=payload
    )

    # You have now received an object that is the unique identifier of your uploaded data
    print(created_structured_data)

    ###################### Reference structured Data ######################
    # With this identifier in combination with your container you can reference your data from anywhere
    structureddata_reference_api = StructureddataReferenceApi(client)
    reference_to_create = StructuredDataReference(
        name="Model props reference",
        structured_data_container_id=container_id,
        structured_data_oids=[created_structured_data.oid],
    )
    created_reference = structureddata_reference_api.create_structured_data_reference(
        collection_id=collection_id,
        data_object_id=dataobject_id,
        structured_data_reference=reference_to_create,
    )
    print(created_reference)
