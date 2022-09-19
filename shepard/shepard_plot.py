from shepard_client.api_client import ApiClient
from shepard_client.configuration import Configuration
from shepard_client.api.timeseries_reference_api import TimeseriesReferenceApi
from shepard_client.api.timeseries_api import TimeseriesApi

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator

HOST = "https://shepard-api.fa-services.intra.dlr.de/shepard/api"
APIKEY = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4NTM1NzE5MS0xZTFiLTQ2MmEtYmQ5OS0xNTUyMGNlZTBjMGEiLCJpc3MiOiJodHRwczovL3NoZXBhcmQtYXBpLmZhLXNlcnZpY2VzLmludHJhLmRsci5kZS9zaGVwYXJkL2FwaS8iLCJuYmYiOjE2NTgxNTAwMTYsImlhdCI6MTY1ODE1MDAxNiwianRpIjoiYjVjOGU2MTEtY2ZmOS00NDI0LWJjMDEtNjE1ZTVmYzFhYjRjIn0.pxDk81-_EI2rF0HJf68yBx7dDO57bDl8WMr1O6-PHmVoompisb3daTQTuf0uPR3bxSFoSNkfRZpTypM6NoOSGmJ94eQPcRZo331MS1vNrhcPqz38tx4J0BiL_2idmh1aSmIDsbzsG8Zcv97mSL5Euh6kWe2DtDnlu-2i1LZmdcTpKbeFI2ixCJMtIy-YL4eNzdUtR41nBsRJpT-vkjeyCoN0zYLnV6DIWf6NnnxJycgZO027MHHcLbovIffNjDSiVgr37BoGQisRazV07bsOfUIjc14qvQlK3CaCP9JLOQ_oJy6tv9SUe00-prMG6U-y1iu1Tzt5EYQ5oApkhIS0_w"

# Set up configuration
conf = Configuration(host=HOST, api_key={"apikey": APIKEY})
conf.access_token = None
client = ApiClient(configuration=conf)

timeseries_api = TimeseriesApi(client)
timeseries_reference_api = TimeseriesReferenceApi(client)

COLLECTION_ID = 13513
CONTAINER_ID = 13985

# timeseries_available = timeseries_api.get_timeseries_available(CONTAINER_ID)

# dataobject_ids = [13841,13849,13857]

# reference_ids = [[13846,13847],[13854,13855],[13862,13863]]


measurements = ["amp_0_wvl_0", "amp_75_wvl_1", "amp_75_wvl_2", "amp_75_wvl_3", "amp_75_wvl_4", "amp_75_wvl_5"]
# measurements = ["amp_75_wvl_1", "amp_75_wvl_2", "amp_75_wvl_3", "amp_75_wvl_4", "amp_75_wvl_5", "amp_50_wvl_3", "amp_75_wvl_3", "amp_100_wvl_3", "amp_200_wvl_3"]

plt.rcParams.update({'font.size': 18})

fig = plt.figure()
# fig.set_size_inches(11.69,8.27)
fig.set_size_inches(9,6)
ax = plt.subplot(111)

for id,measurement in enumerate(measurements):

    displacement_timeseries1 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output1_External_Displacement",
        field="value",
        start=0,
        end=10000000,
    )
    force_timeseries1 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output1_External_Force",
        field="value",
        start=0,
        end=10000000,
    )

    displacement_timeseries2 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output2_External_Displacement",
        field="value",
        start=0,
        end=10000000,
    )
    force_timeseries2 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output2_External_Force",
        field="value",
        start=0,
        end=10000000,
    )

    factor = int(1e9)

    time = []
    displacement = []
    force = []

    for displ_point, force_point in zip(displacement_timeseries1.points, force_timeseries1.points):
        time.append(force_point.timestamp / factor)
        displacement.append(displ_point.value)
        force.append(abs(force_point.value))

    for displ_point, force_point in zip(displacement_timeseries2.points, force_timeseries2.points):
        if force_point.timestamp / factor > time[-1]:
            time.append(force_point.timestamp / factor)
            displacement.append(displ_point.value)
            force.append(abs(force_point.value))

    ax.plot(displacement, force, label=measurement)
    ax.xaxis.set_major_locator(MaxNLocator(5)) 
    # ax.plot(displacement, force, linestyle="dashed")

ax.legend()

plt.xlabel("Displacement [mm]")
plt.ylabel("Force [N]")

plt.show()
fig.savefig("DisplForceWvl.png")


measurements = ["amp_0_wvl_0", "amp_50_wvl_3", "amp_75_wvl_3", "amp_100_wvl_3", "amp_200_wvl_3"]

fig = plt.figure()
# fig.set_size_inches(11.69,8.27)
fig.set_size_inches(9,6)
ax = plt.subplot(111)

for id,measurement in enumerate(measurements):

    displacement_timeseries1 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output1_External_Displacement",
        field="value",
        start=0,
        end=10000000,
    )
    force_timeseries1 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output1_External_Force",
        field="value",
        start=0,
        end=10000000,
    )

    displacement_timeseries2 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output2_External_Displacement",
        field="value",
        start=0,
        end=10000000,
    )
    force_timeseries2 = timeseries_api.get_timeseries(
        CONTAINER_ID,
        measurement=measurement,
        location="None",
        device="Peridigm",
        symbolic_name="Smetana_Output2_External_Force",
        field="value",
        start=0,
        end=10000000,
    )

    factor = int(1e9)

    time = []
    displacement = []
    force = []

    # ax.plot(displacement, force, label=measurement)
    # displacement = []
    # force = []

    for displ_point, force_point in zip(displacement_timeseries1.points, force_timeseries1.points):
        time.append(force_point.timestamp / factor)
        displacement.append(displ_point.value)
        force.append(abs(force_point.value))

    for displ_point, force_point in zip(displacement_timeseries2.points, force_timeseries2.points):
        if force_point.timestamp / factor > time[-1]:
            time.append(force_point.timestamp / factor)
            displacement.append(displ_point.value)
            force.append(abs(force_point.value))

    ax.plot(displacement, force, label=measurement)
    ax.xaxis.set_major_locator(MaxNLocator(5)) 
    # ax.plot(displacement, force, linestyle="dashed")

ax.legend()

plt.xlabel("Displacement [mm]")
plt.ylabel("Force [N]")

plt.show()
fig.savefig("DisplForceAmp.png")