import os

from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration

from shepard_client.api.structureddata_api import StructureddataApi
from shepard_client.models.structured_data_payload import StructuredDataPayload
from shepard_client.models.structured_data import StructuredData
from shepard_client.api.structureddata_reference_api import StructureddataReferenceApi
from shepard_client.models.structured_data_reference import StructuredDataReference

HOST = "https://shepard-api.fa-services.intra.dlr.de/shepard/api"
# APIKEY = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4NTM1NzE5MS0xZTFiLTQ2MmEtYmQ5OS0xNTUyMGNlZTBjMGEiLCJpc3MiOiJodHRwczovL3NoZXBhcmQtYXBpLmZhLXNlcnZpY2VzLmludHJhLmRsci5kZS9zaGVwYXJkL2FwaS8iLCJuYmYiOjE2NTgxNTAwMTYsImlhdCI6MTY1ODE1MDAxNiwianRpIjoiYjVjOGU2MTEtY2ZmOS00NDI0LWJjMDEtNjE1ZTVmYzFhYjRjIn0.pxDk81-_EI2rF0HJf68yBx7dDO57bDl8WMr1O6-PHmVoompisb3daTQTuf0uPR3bxSFoSNkfRZpTypM6NoOSGmJ94eQPcRZo331MS1vNrhcPqz38tx4J0BiL_2idmh1aSmIDsbzsG8Zcv97mSL5Euh6kWe2DtDnlu-2i1LZmdcTpKbeFI2ixCJMtIy-YL4eNzdUtR41nBsRJpT-vkjeyCoN0zYLnV6DIWf6NnnxJycgZO027MHHcLbovIffNjDSiVgr37BoGQisRazV07bsOfUIjc14qvQlK3CaCP9JLOQ_oJy6tv9SUe00-prMG6U-y1iu1Tzt5EYQ5oApkhIS0_w"
APIKEY = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIyYTNmODM4YS1iNjU5LTRkMTgtYmYxMy0wNTkwOTgyMWZmMzQiLCJpc3MiOiJodHRwczovL3NoZXBhcmQtYXBpLmZhLXNlcnZpY2VzLmludHJhLmRsci5kZS9zaGVwYXJkL2FwaS8iLCJuYmYiOjE2NjkzMDM2ODQsImlhdCI6MTY2OTMwMzY4NCwianRpIjoiYTI3ZDQ0ODMtYTk4My00OTVhLTk5OGItNTA0OTA1MTNkY2M0In0.gwmamIIEAOah7M1bzK8Y5wwIHq-BmRb3-GlyCZl7PvsokTU3EuW-HRfHfRWq6z53v8iykyMg69B5hbiwv8nt2vVP3h86nOMUlZ1SwqL1VJGwSH1aLBDbNT2_RP-CR5mPITcnziQiERPNhy5ppX-ct-BpV3eRWnWCL0YKQJg2TYvzea53Re-VRGH0v-Je3HxpUISmsUBN56iQI8DEb94Vc9nYv_rdEB4cs9zmeYAV7CGTonE5aA6eWiyQRd-VtJ2uQnAQQz4Q9SJvU5s6ks4rPyHylwRVPirJMBCtfZnKd9wbdyUoG_zm67Yu_37RwviTuVdjlrhCOto0Ql1I8mFI8A"
# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

# In order to upload structured data, you first need to create a container into which you can upload your data
structureddata_api = StructureddataApi(client)

collection_id = 12187
# dataobject_id = 12196
dataobject_id = 12211
container_id = 12189

# Read local json data
model = "Kalthoff-Winkler"
# model = "Smetana"
path = "gui/app/src/assets/models"
# for model in next(os.walk(path))[1]:
    
with open(os.path.join(path, model, model + ".json"), "r", encoding="UTF-8") as file:
    response = file.read()

    ###################### Structured Data ######################
    # Now you can upload some data into your newly created container
    payload = StructuredDataPayload(
        structured_data=StructuredData(name=model),
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
        name="Model data reference",
        structured_data_container_id=container_id,
        structured_data_oids=[created_structured_data.oid],
    )
    created_reference = structureddata_reference_api.create_structured_data_reference(
        collection_id=collection_id,
        data_object_id=dataobject_id,
        structured_data_reference=reference_to_create,
    )
    print(created_reference)