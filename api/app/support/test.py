# import vtk
# from vtk.util.numpy_support import vtk_to_numpy
import math
import numpy as np
import re
import json
import netCDF4
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

from exodus_reader import ExodusReader


def arclength(X, Y, a, b):
    """
    Computes the arclength of the given curve
    defined by (x0, y0), (x1, y1) ... (xn, yn)
    over the provided bounds, `a` and `b`.

    Parameters
    ----------
    x: numpy.ndarray
        The array of x values

    y: numpy.ndarray
        The array of y values corresponding to each value of x

    a: int
        The lower limit to integrate from

    b: int
        The upper limit to integrate to

    Returns
    -------
    numpy.float64
        The arclength of the curve

    """
    bounds = (X >= a) & (Y <= b)

    arclength = np.trapz(np.sqrt(1 + np.gradient(Y[bounds], X[bounds]) ** 2), X[bounds])
    cracklength = arclength

    return cracklength


def getCrackLength(points, damage):

    x = points[:, 0]
    y = points[:, 1]
    # X_result = []
    # Y_result = []
    # Crack_length = []
    # K1 = []
    # for x, y, damage in zip(X, Y, Damage):

    sample_weight = damage  # / max(damage)
    x = np.asarray(x).reshape(len(x), 1)
    y = np.asarray(y).reshape(len(x), 1)

    # # The unweighted model
    # regr = LinearRegression()
    # regr.fit(X, Y)
    # plt.plot(
    #     X, regr.predict(X), color="blue", linewidth=1, label="Unweighted model"
    # )

    # # The weighted model
    # regr = LinearRegression()
    # regr.fit(X, Y, sample_weight)
    # plt.plot(X, regr.predict(X), color="red", linewidth=1, label="Weighted model")

    # # The weighted model - scaled weights
    # regr = LinearRegression()
    # sample_weight = sample_weight  # / max(sample_weight)
    # regr.fit(X, Y, sample_weight)
    # plt.plot(
    #     X,
    #     regr.predict(X),
    #     color="yellow",
    #     linewidth=1,
    #     label="Weighted model - scaled",
    # )

    # The poly model
    regr = LinearRegression()
    poly_reg = PolynomialFeatures(degree=2)
    x_poly = poly_reg.fit_transform(x)
    regr.fit(x_poly, y, sample_weight)
    plt.plot(
        x,
        regr.predict(x_poly),
        color="green",
        linewidth=1,
        label="Polynomial weighted model",
    )
    # X_result.append(x)
    # Y_result.append(regr.predict(x_poly))
    # plt.scatter(x, y, s=damage)

    # plt.xticks(())
    # plt.yticks(())
    # plt.legend()

    plt.axis([x_min, x_max, y_min, y_max])
    plt.show()
    # plt.savefig("test.png")

    # arc_length = arclength(X[:, 0], regr.predict(X_poly)[:, 0], 0, 100)
    arc_length = arclength(np.array(x), np.array(regr.predict(x_poly)), 0, 100)
    print(arc_length)
    # Crack_length.append(arc_length)
    # K1.append(k1)

    # plt.plot(range(0, len(Crack_length)), Crack_length)
    # image_file = os.path.join(resultpath, model_name + "_" + output + "_crack.png")
    # plt.savefig(image_file)
    # plt.show
    # response = [time, Crack_length, K1]
    return arc_length


def calculate_k1(P, B, W, a):

    k1 = (
        P
        / B
        * (math.sqrt(math.pi / W))
        * (
            16.7 * math.pow(a / W, 1 / 2)
            - 104.7 * math.pow(a / W, 3 / 2)
            + 369.9 * math.pow(a / W, 5 / 2)
            - 537.8 * math.pow(a / W, 7 / 2)
            + 360.5 * math.pow(a / W, 9 / 2)
        )
    )
    return k1

def createFigure(xE,yE, name = 'Strain_belt.pdf'):
    fig = plt.figure(figsize=(14/2.54, 12/2.54))
    plt.plot(xE,yE, color='black', linestyle='solid')
    plt.grid(which='major', axis='both')
    plt.xlabel(r'$u_y$ [m]')
    plt.ylabel(r'$F_y$ [N]')
    
    plt.rcParams.update({'font.size': 8})
    plt.tight_layout()

    ax=plt.gca()
    ax.legend(loc='best')
    ax.xaxis.set
    # ax.set_xlim([min(xE), max(xE)])

    fig.savefig(name,bbox_inches='tight')
    plt.show()

P = 3780
a = 35.0
d = 0.00000023
w = 10
L = 37.1

resultpath = "/home/jt/perihub/api/app/Output/CompactTension/CompactTension_Output1.e"
# resultpath = "/mnt/c/Users/hess_ja/Desktop/DockerProjects/periHubVolumes/peridigmJobs/dev/CompactTension/CompactTension_Output1.e"
resultpath = "/mnt/c/Users/hess_ja/Desktop/DockerProjects/periHubVolumes/peridigmJobs/dev/Smetana_Output1.e"
# resultpath = "/home/jt/perihub/api/app/Output/GIICmodel/GIICmodel_Output1.e"

variable= "External_Force"
axis = "X"
global_data, time = ExodusReader.read(resultpath)

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
# x_min = 28
# x_max = 100
# y_min = -100
# y_max = 100
x_min = 50.8
x_max = 90
y_min = 1
y_max = 2.8
# # file = os.path.join(resultpath, model_name + "_" + output + ".e")
# # print(file)

# reader = vtk.vtkExodusIIReader()
# reader.SetFileName(resultpath)
# vtk_mesh = _read_exodusii_mesh(reader, 10)
# points = vtk_to_numpy(vtk_mesh.GetPoints().GetData())
# cells = _read_cells(vtk_mesh)
# point_data = _read_data(vtk_mesh.GetPointData())
# cell_data = _read_data(vtk_mesh.GetCellData())
# field_data = _read_data(vtk_mesh.GetFieldData())

# # print(points)
# # print(cells)
# # print(point_data)
# # print(cell_data)
# # print(field_data)

min_damage = 0.007

Crack_length = []
K1 = []
Load = []
Force = []
Displacement = []

points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(resultpath, 0)

first_time = time.data.item()
first_displ = global_data["External_Displacement"][0]
first_force = global_data["External_Force"][0]
damage_blocks = cell_data["Damage"][0]

first_damage_id = []
for block_id, _ in enumerate(block_data):
    if block_id in damage_blocks:
        if np.max(damage_blocks[block_id]) > 0:
            first_damage_id.append(block_id)
    
            block_ids = block_data[block_id][:, 0]
            block_points = points[block_ids]
            filter = (damage_blocks[block_id] > 0.0)
            current_points = block_points + point_data["Displacement"][block_ids]

            filtered_points = current_points[filter]

points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(resultpath, -1)

last_time = time.data.item()
last_displ = global_data["External_Displacement"][0]
last_force = global_data["External_Force"][0]
damage_blocks = cell_data["Damage"][0]

last_damage_id = []
for block_id, _ in enumerate(block_data):
    if block_id in damage_blocks:
        if np.max(damage_blocks[block_id]) > 0:
            last_damage_id.append(block_id)

result_dict = {
    "first_damage": {
        "time": first_time,
        "block_id": first_damage_id,
        "displacement": {
            "x": first_displ[0],
            "y": first_displ[1],
            "z": first_displ[2]
        },
        "force": {
            "x": first_force[0],
            "y": first_force[1],
            "z": first_force[2]
        },
        "points": {
            "x": filtered_points[0][0],
            "y": filtered_points[0][1],
            "z": filtered_points[0][2]
        }
    },
    "last_ply_failure": {
        "time": last_time,
        "block_id": last_damage_id,
        "displacement": {
            "x": last_displ[0],
            "y": last_displ[1],
            "z": last_displ[2]
        },
        "force": {
            "x": last_force[0],
            "y": last_force[1],
            "z": last_force[2]
        }
    }
}

json_path = "Test.json"

with open(json_path, "w") as file:
    json.dump(result_dict, file)

variable = "Damage"
axis = "x"
displ_factor=0
marker_size= 47
height=10
length=50
use_cell_data=False

if variable in ['Damage','Partial_StressX','Partial_StressY','Partial_StressZ', 'Number_Of_Neighbors']:
    use_cell_data=True

axis_id=0

if axis == 'x':
    axis_id=0
    if 'Partial_Stress' in variable:
        variable = variable + 'X'
elif axis == 'y':
    axis_id=1
    if 'Partial_Stress' in variable:
        variable = variable + 'Y'
elif axis == 'z':
    axis_id=2
    if 'Partial_Stress' in variable:
        variable = variable + 'Z'
elif axis == 'Magnitude':
    axis_id=0

fig, ax = plt.subplots()

if use_cell_data:
    min_value = min(cell_data[variable][0][0])
    max_value = max(cell_data[variable][0][0])
    for block_id in range(1,len(block_data)):
        if block_id in cell_data[variable][0]:
        # if len(cell_data[variable][0][block_id])>0:
            if min(cell_data[variable][0][block_id]) < min_value:
                min_value = min(cell_data[variable][0][block_id])
            if max(cell_data[variable][0][block_id]) > max_value:
                max_value = max(cell_data[variable][0][block_id])
    for block_id in range(0,len(block_data)):

        block_ids = block_data[block_id][:, 0]

        block_points = points[block_ids]

        np_first_points_x = np.array(block_points[:, 0])
        np_first_points_y = np.array(block_points[:, 1])
        np_displacement_x = np.array(point_data['Displacement'][block_ids,0])
        np_displacement_y = np.array(point_data['Displacement'][block_ids,1])

        np_points_x = np.add(np_first_points_x, np.multiply(np_displacement_x, displ_factor))
        np_points_y = np.add(np_first_points_y, np.multiply(np_displacement_y, displ_factor))
        
        if block_id in cell_data[variable][0] and max(cell_data[variable][0][block_id]) > 0:
            scatter = ax.scatter(np_points_x, np_points_y, c=cell_data[variable][0][block_id], cmap=cm.jet, s=marker_size, vmin=min_value, vmax=max_value)
        else:
            scatter = ax.scatter(np_points_x, np_points_y, c=np.full_like(np_points_x,0), cmap=cm.jet, s=marker_size)

else:
    np_first_points_x = np.array(points[:, 0])
    np_first_points_y = np.array(points[:, 1])
    np_displacement_x = np.array(point_data['Displacement'][:,0])
    np_displacement_y = np.array(point_data['Displacement'][:,1])

    np_points_x = np.add(np_first_points_x, np.multiply(np_displacement_x, displ_factor))
    np_points_y = np.add(np_first_points_y, np.multiply(np_displacement_y, displ_factor))

    scatter = ax.scatter(np_points_x, np_points_y, c=point_data[variable][:,axis_id], cmap=cm.jet, s=marker_size)

# COLORBAR
cbar = fig.colorbar(scatter, ax=ax)

# set colorbar label plus label color
cbar.set_label(variable + '_' + axis, color='black')

# set colorbar tick color
cbar.ax.yaxis.set_tick_params(color='black')

# set colorbar edgecolor 
cbar.outline.set_edgecolor('black')

fig.set_size_inches(18.5, 18.5 * (height/length))

# filepath = ''
# if 'Partial_Stress' in variable:
#     filepath = file[:-2] + '_' + variable[:-1] + '_' + axis + '.png'
#     fig.savefig(filepath, dpi=400)
# else:
#     filepath = file[:-2] + '_' + variable + '_' + axis + '.png'
#     fig.savefig(filepath, dpi=400)

# plt.colorbar()
plt.show()

# first_displ = global_data["External_Displacement"][0]
# first_force = global_data["External_Force"][0]
# damage_blocks = cell_data["Damage"]

# first_damage_id = []
# for id, damage_block in enumerate(damage_blocks):
#     if len(damage_block)!=0:
#         if np.max(damage_block) > 0:
#             first_damage_id.append(id)
            
#             block_ids = block_data[id][:, 0]
#             block_points = points[block_ids]
#             filter = (cell_data["Damage"][id] > 0.0)
#             current_points = block_points + point_data["Displacement"][block_ids]

#             filtered_points = current_points[filter]

# result_dict = {
#             "first_ply_failure": {
#                 "block_id": first_damage_id,
#                 "displacement": {
#                     "x": first_displ[0],
#                     "y": first_displ[1],
#                     "z": first_displ[2],
#                 },
#                 "force": {
#                     "x": first_force[0],
#                     "y": first_force[1],
#                     "z": first_force[2],
#                 },
#                 "points": {
#                     "x": filtered_points[0][0],
#                     "y": filtered_points[0][1],
#                     "z": filtered_points[0][2],
#                 }
#             }
#         }
# json_path = "Test.json"

# with open(json_path, "w") as file:
#     json.dump(result_dict, file)

for i in range(0, 100):
    points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(resultpath, i)
    # block_ids = block_data[0][:, 0]

    # block_points = points[block_ids]

    # filter = (
    #     (x_min <= block_points[:, 0])
    #     & (block_points[:, 0] <= x_max)
    #     & (y_min <= block_points[:, 1])
    #     & (block_points[:, 1] <= y_max)
    #     & (cell_data["Damage"][0] >= min_damage)
    # )
    # current_points = block_points + point_data["Displacement"][block_ids]

    # filtered_points = current_points[filter]
    # filtered_damage = cell_data["Damage"][0][filter]
    # # print(filtered_points)
    # # print(filtered_damage)

    # if np.any(filtered_points) and len(filtered_points) >= 25:
    #     crack_length = getCrackLength(filtered_points, filtered_damage)
    #     load = global_data["External_Force"][0] * 0.1 * w
    #     Load.append(load)
    #     k1 = calculate_k1(load, 10, 50, crack_length)
    #     # print(k1)
    #     Crack_length.append(crack_length)
    #     K1.append(k1)
    # else:
    #     Crack_length.append(0)
    #     K1.append(0)
    #     Load.append(0)

    # print(global_data["External_Force"][0])
    # Force.append(global_data["Crosshead_Force"][1])
    # Displacement.append(-global_data["Crosshead_Displacement"][1])
    Force.append(-global_data["External_Force_2"][1])
    Displacement.append(global_data["External_Displacement_2"][1])
    # P = global_data["Crosshead_Force"][1]
    # d = global_data["Crosshead_Displacement"][1]
    GIIC = (9 * P * math.pow(a, 2) * d * 1000) / (
        2 * w * (1 / 4 * math.pow(L, 3) + 3 * math.pow(a, 3))
    )
    # print(GIIC)

# idx = 0
# crack_acceleration = [0]
# delta_k1 = [0]
# delta_load = [0]
# for idx in range(0, len(Crack_length)):
#     if idx != 0:
#         crack_acceleration.append(Crack_length[idx] - Crack_length[idx - 1])
#         delta_k1.append(K1[idx] - K1[idx - 1])
#         delta_load.append(Load[idx] - Load[idx - 1])


# plt.plot(Load, Crack_length)
# plt.show
# plt.plot(range(0, len(Crack_length)), crack_acceleration)
# plt.plot(Displacement, Force)
# plt.plot(delta_k1, crack_acceleration)
# plt.plot(range(0, len(Crack_length)), Load)
# plt.show

# data = {'Force_Y':Force,'Displacement_Y':Displacement}

# df = pd.DataFrame(data)

# df.to_csv('Curve.csv')

createFigure(Displacement, Force, 'Displ_Force_CT.pdf')