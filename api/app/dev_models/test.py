# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import os

import matplotlib.pyplot as plt
import numpy as np
from exodusreader.exodusreader import ExodusReader


def get_global_data(file, variable, axis, absolute):
    (
        points,
        point_data,
        global_data,
        cell_data,
        ns,
        block_data,
        time,
    ) = ExodusReader.read(file)

    if variable == "Time":
        data = time
    else:
        if absolute:
            if axis == "X":
                data = [item[0] for item in abs(global_data[variable])]
            elif axis == "Y":
                data = [item[1] for item in abs(global_data[variable])]
            elif axis == "Z":
                data = [item[2] for item in abs(global_data[variable])]
            elif axis == "Magnitude":
                data = [item[0] for item in abs(global_data[variable])]
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


# resultpath = "/home/jt/perihub/api/app/Output/CompactTension/CompactTension_Output1.e"
resultpath = "/mnt/c/Users/hess_ja/Desktop/DockerProjects/periHubVolumes/peridigmJobs/dev"

model_name = "CompactTension"

resultpath = os.path.join(resultpath, model_name)

file = os.path.join(resultpath, model_name + "_Output1.e")
file2 = os.path.join(resultpath, model_name + "_Output2.e")

(
    points,
    point_data,
    global_data,
    cell_data,
    ns,
    block_data,
    time,
) = ExodusReader.read(file)

Force = get_global_data(file, "External_Force", "Y", True)
Displ = get_global_data(file, "External_Displacement", "Y", True)

Force2 = get_global_data(file2, "External_Force", "Y", True)
Displ2 = get_global_data(file2, "External_Displacement", "Y", True)

fig, ax = plt.subplots()

ax.plot(Displ, Force)
ax.set_xlabel("Displacement [mm]")
ax.set_ylabel("Force [N]")
ax.set_xlim(0)
ax.set_ylim(0)

fig.set_size_inches(8, 6)

ax.fill_between(Displ, Force, 0, where=Displ < Displ2[0], color="gray", alpha=0.5)

half_displ = max(Displ) / 2

np_displ = np.array(Displ)
index = np.where(np_displ + 1e-9 > half_displ)

ax.text(
    half_displ,
    Force[index[0][0]] / 2,
    r"$W_B\, [J]$",
    size=12,
    ha="center",
    va="center",
)

plt.show
