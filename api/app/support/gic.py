import math
from exodusreader.exodusreader import ExodusReader

w=2
a=5
h=1.5
C1=3.467
C2=2.315

resultpath = "/mnt/c/Users/hess_ja/Desktop/DockerProjects/periHubVolumes/peridigmJobs/dev/GICmodel/GICmodel_Output2.e"

points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(resultpath, 0)

P_low = abs(global_data["Lower_Load_Force"][0][1])
P_up = abs(global_data["Upper_Load_Force"][0][1])
d_low = abs(global_data["Lower_Load_Displacement"][0][1])
d_up = abs(global_data["Upper_Load_Displacement"][0][1])

delta = d_up + d_low
P = (P_up + P_low)/2

Delta = 1

print(P_low)
print(P_up)
print(d_low)
print(d_up)
print(delta)
print(w)
print(a)

GIC = (3 * P * delta) / (
    2 * w * (a + abs(Delta))
)

print(GIC)