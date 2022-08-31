from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration
from shepard_client.api.timeseries_reference_api import TimeseriesReferenceApi

import matplotlib.pyplot as plt

HOST = "https://shepard-api.fa-services.intra.dlr.de/shepard/api"
APIKEY = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4NTM1NzE5MS0xZTFiLTQ2MmEtYmQ5OS0xNTUyMGNlZTBjMGEiLCJpc3MiOiJodHRwczovL3NoZXBhcmQtYXBpLmZhLXNlcnZpY2VzLmludHJhLmRsci5kZS9zaGVwYXJkL2FwaS8iLCJuYmYiOjE2NTgxNTAwMTYsImlhdCI6MTY1ODE1MDAxNiwianRpIjoiYjVjOGU2MTEtY2ZmOS00NDI0LWJjMDEtNjE1ZTVmYzFhYjRjIn0.pxDk81-_EI2rF0HJf68yBx7dDO57bDl8WMr1O6-PHmVoompisb3daTQTuf0uPR3bxSFoSNkfRZpTypM6NoOSGmJ94eQPcRZo331MS1vNrhcPqz38tx4J0BiL_2idmh1aSmIDsbzsG8Zcv97mSL5Euh6kWe2DtDnlu-2i1LZmdcTpKbeFI2ixCJMtIy-YL4eNzdUtR41nBsRJpT-vkjeyCoN0zYLnV6DIWf6NnnxJycgZO027MHHcLbovIffNjDSiVgr37BoGQisRazV07bsOfUIjc14qvQlK3CaCP9JLOQ_oJy6tv9SUe00-prMG6U-y1iu1Tzt5EYQ5oApkhIS0_w"

# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

timeseries_reference_api = TimeseriesReferenceApi(client)

COLLECTION_ID = 13513

dataobject_ids = [13841,13849,13857]

reference_ids = [[13846,13847],[13854,13855],[13862,13863]]

fig = plt.figure()
ax = plt.subplot(111)

for dataobject_id, reference_id in zip(dataobject_ids,reference_ids):

    displacement_timeseries = timeseries_reference_api.get_timeseries_payload(
        collection_id=COLLECTION_ID,
        data_object_id=dataobject_id,
        timeseries_reference_id=reference_id[0],
    )

    force_timeseries = timeseries_reference_api.get_timeseries_payload(
        collection_id=COLLECTION_ID,
        data_object_id=dataobject_id,
        timeseries_reference_id=reference_id[1],
    )

    factor = int(1e9)

    time = []
    displacement = []
    force = []
    for displ_point, force_point in zip(displacement_timeseries[0].points, force_timeseries[0].points):
        time.append(force_point.timestamp / factor)
        displacement.append(displ_point.value)
        force.append(force_point.value)

    ax.plot(displacement, force, label=displacement_timeseries[0].timeseries.measurement)

ax.legend()

plt.xlabel("Displacement")
plt.ylabel("Force")

plt.show()
