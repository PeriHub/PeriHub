import time
from math import radians, sin

from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration

from shepard_client.api.timeseries_api import TimeseriesApi
from shepard_client.models.timeseries_container import TimeseriesContainer
from shepard_client.models.timeseries_payload import TimeseriesPayload
from shepard_client.models.timeseries import Timeseries
from shepard_client.models.influx_point import InfluxPoint
from shepard_client.api.timeseries_reference_api import TimeseriesReferenceApi
from shepard_client.models.timeseries_reference import TimeseriesReference

from api.app.support.exodus_reader import ExodusReader

class Analysis:
    @staticmethod
    def get_global_data(file, variable, axis):

        global_data, time = ExodusReader.read(file)

        if variable == "Time":
            data = time
        else:
            if axis == "X":
                data = [item[0] for item in global_data[variable]]
            elif axis == "Y":
                data = [item[1] for item in global_data[variable]]
            elif axis == "Z":
                data = [item[2] for item in global_data[variable]]
            elif axis == "Magnitude":
                data = [item[0] for item in global_data[variable]]
        return data

HOST = "https://shepard-api.fa-services.intra.dlr.de/shepard/api"
APIKEY = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4NTM1NzE5MS0xZTFiLTQ2MmEtYmQ5OS0xNTUyMGNlZTBjMGEiLCJpc3MiOiJodHRwczovL3NoZXBhcmQtYXBpLmZhLXNlcnZpY2VzLmludHJhLmRsci5kZS9zaGVwYXJkL2FwaS8iLCJuYmYiOjE2NTgxNTAwMTYsImlhdCI6MTY1ODE1MDAxNiwianRpIjoiYjVjOGU2MTEtY2ZmOS00NDI0LWJjMDEtNjE1ZTVmYzFhYjRjIn0.pxDk81-_EI2rF0HJf68yBx7dDO57bDl8WMr1O6-PHmVoompisb3daTQTuf0uPR3bxSFoSNkfRZpTypM6NoOSGmJ94eQPcRZo331MS1vNrhcPqz38tx4J0BiL_2idmh1aSmIDsbzsG8Zcv97mSL5Euh6kWe2DtDnlu-2i1LZmdcTpKbeFI2ixCJMtIy-YL4eNzdUtR41nBsRJpT-vkjeyCoN0zYLnV6DIWf6NnnxJycgZO027MHHcLbovIffNjDSiVgr37BoGQisRazV07bsOfUIjc14qvQlK3CaCP9JLOQ_oJy6tv9SUe00-prMG6U-y1iu1Tzt5EYQ5oApkhIS0_w"

# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

collection_id = 13513
container_id = 13539
dataobject_id = 13552

# In order to upload timeseries, you first need to create a container into which you can upload your data
timeseries_api = TimeseriesApi(client)
# container_to_create = TimeseriesContainer(name="MyFirstTimeseriesContainer")
# created_container = timeseries_api.create_timeseries_container(
#     timeseries_container=container_to_create
# )

# Now you can upload some data into your newly created container

resultpath = "/mnt/c/Users/hess_ja/Desktop/DockerProjects/periHubVolumes/peridigmJobs/dev/GICmodel/GICmodel_Output2.e"

variable= "Lower_Load_Force"

global_data = Analysis.get_global_data(resultpath, variable,  "X")
global_time = Analysis.get_global_data(resultpath, "Time", "")

factor = int(1e9)

points = []

for i, seconds in enumerate(global_time):
    value = global_data[i]
    timestamp = seconds * factor
    points.append(InfluxPoint(value=value, timestamp=timestamp))

timeseries = Timeseries(
    measurement=variable,
    location="MyLoc",
    device="MyDev",
    symbolic_name="MySymName",
    field="value",
)
payload = TimeseriesPayload(timeseries=timeseries, points=points)
created_timeseries = timeseries_api.create_timeseries(
    timeseries_container_id=container_id, timeseries_payload=payload
)
# You have now received an object that is the unique identifier of your uploaded timeseries
print(created_timeseries)

timeseries_reference_api = TimeseriesReferenceApi(client)
reference_to_create = TimeseriesReference(
    name="MyFirstReference",
    start=points[0].timestamp,
    end=points[-1].timestamp,
    timeseries_container_id=container_id,
    timeseries=[created_timeseries],
)
created_reference = timeseries_reference_api.create_timeseries_reference(
    collection_id=collection_id,
    data_object_id=dataobject_id,
    timeseries_reference=reference_to_create,
)

# # See which time series are available in the container
# timeseries_available = timeseries_api.get_timeseries_available(container_id)
# print(timeseries_available)

# # Retrieve your data
# timeseries_payload = timeseries_api.get_timeseries(
#     container_id,
#     measurement=variable,
#     location="MyLoc",
#     device="MyDev",
#     symbolic_name="MySymName",
#     field="value",
#     start=points[0].timestamp,
#     end=points[-1].timestamp,
# )
# print(len(timeseries_payload.points))
