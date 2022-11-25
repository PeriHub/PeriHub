from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration

from shepard_client.api.collection_api import CollectionApi
from shepard_client.api.file_api import FileApi
from shepard_client.api.structureddata_api import StructureddataApi
from shepard_client.api.timeseries_api import TimeseriesApi

HOST = "https://shepard-api.fa-services.intra.dlr.de/shepard/api"
APIKEY = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4NTM1NzE5MS0xZTFiLTQ2MmEtYmQ5OS0xNTUyMGNlZTBjMGEiLCJpc3MiOiJodHRwczovL3NoZXBhcmQtYXBpLmZhLXNlcnZpY2VzLmludHJhLmRsci5kZS9zaGVwYXJkL2FwaS8iLCJuYmYiOjE2NTgxNTAwMTYsImlhdCI6MTY1ODE1MDAxNiwianRpIjoiYjVjOGU2MTEtY2ZmOS00NDI0LWJjMDEtNjE1ZTVmYzFhYjRjIn0.pxDk81-_EI2rF0HJf68yBx7dDO57bDl8WMr1O6-PHmVoompisb3daTQTuf0uPR3bxSFoSNkfRZpTypM6NoOSGmJ94eQPcRZo331MS1vNrhcPqz38tx4J0BiL_2idmh1aSmIDsbzsG8Zcv97mSL5Euh6kWe2DtDnlu-2i1LZmdcTpKbeFI2ixCJMtIy-YL4eNzdUtR41nBsRJpT-vkjeyCoN0zYLnV6DIWf6NnnxJycgZO027MHHcLbovIffNjDSiVgr37BoGQisRazV07bsOfUIjc14qvQlK3CaCP9JLOQ_oJy6tv9SUe00-prMG6U-y1iu1Tzt5EYQ5oApkhIS0_w"

def set_permission(permission,api,id):

    if permission.permission_type == 'Private':
        permission.permission_type = 'Public'
        permission = api.edit_collection_permissions(collection_id=id, permissions=permission)

        print(permission)

conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

collection_api = CollectionApi(client)
file_api = FileApi(client)
structureddata_api = StructureddataApi(client)
timeseries_api = TimeseriesApi(client)

for i in range(12000,15000):
    print(i)
    try:
        collection_permissions = collection_api.get_collection_permissions(collection_id=i)
        if collection_permissions.permission_type == 'Private':
            collection_permissions.permission_type = 'Public'
            collection_permissions = collection_api.edit_collection_permissions(collection_id=i, permissions=collection_permissions)
            print(collection_permissions)
        continue
    except: 
        pass

    try:
        file_permissions = file_api.get_file_permissions(file_container_id=i)
        if file_permissions.permission_type == 'Private':
            file_permissions.permission_type = 'Public'
            file_permissions = file_api.edit_file_permissions(file_container_id=i, permissions=file_permissions)
            print(file_permissions)
        continue
    except: 
        pass

    try:
        structureddata_permissions = structureddata_api.get_structured_data_permissions(structureddata_container_id=i)
        if structureddata_permissions.permission_type == 'Private':
            structureddata_permissions.permission_type = 'Public'
            structureddata_permissions = structureddata_api.edit_structured_data_permissions(structureddata_container_id=i, permissions=structureddata_permissions)
            print(structureddata_permissions)
        continue
    except: 
        pass

    try:
        timeseries_permissions = timeseries_api.get_timeseries_permissions(timeseries_container_id=i)
        if timeseries_permissions.permission_type == 'Private':
            timeseries_permissions.permission_type = 'Public'
            timeseries_permissions = timeseries_api.edit_timeseries_permissions(timeseries_container_id=i, permissions=timeseries_permissions)
            print(timeseries_permissions)
        continue
    except: 
        pass