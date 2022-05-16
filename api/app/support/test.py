# import vtk
# from vtk.util.numpy_support import vtk_to_numpy
import math
import numpy as np
import re
import netCDF4
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


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


exodus_to_meshio_type = {
    "SPHERE": "vertex",
    # curves
    "BEAM": "line",
    "BEAM2": "line",
    "BEAM3": "line3",
    "BAR2": "line",
    # surfaces
    "SHELL": "quad",
    "SHELL4": "quad",
    "SHELL8": "quad8",
    "SHELL9": "quad9",
    "QUAD": "quad",
    "QUAD4": "quad",
    "QUAD5": "quad5",
    "QUAD8": "quad8",
    "QUAD9": "quad9",
    #
    "TRI": "triangle",
    "TRIANGLE": "triangle",
    "TRI3": "triangle",
    "TRI6": "triangle6",
    "TRI7": "triangle7",
    # 'TRISHELL': 'triangle',
    # 'TRISHELL3': 'triangle',
    # 'TRISHELL6': 'triangle6',
    # 'TRISHELL7': 'triangle',
    #
    # volumes
    "HEX": "hexahedron",
    "HEXAHEDRON": "hexahedron",
    "HEX8": "hexahedron",
    "HEX9": "hexahedron9",
    "HEX20": "hexahedron20",
    "HEX27": "hexahedron27",
    #
    "TETRA": "tetra",
    "TETRA4": "tetra4",
    "TET4": "tetra4",
    "TETRA8": "tetra8",
    "TETRA10": "tetra10",
    "TETRA14": "tetra14",
    #
    "PYRAMID": "pyramid",
    "WEDGE": "wedge",
}
meshio_to_exodus_type = {v: k for k, v in exodus_to_meshio_type.items()}


def categorize(names):
    # Check if there are any <name>R, <name>Z tuples or <name>X, <name>Y, <name>Z
    # triplets in the point data. If yes, they belong together.
    single = []
    double = []
    triple = []
    is_accounted_for = [False] * len(names)
    k = 0
    while True:
        if k == len(names):
            break
        if is_accounted_for[k]:
            k += 1
            continue
        name = names[k]
        if name[-1] == "X":
            ix = k
            try:
                iy = names.index(name[:-1] + "Y")
            except ValueError:
                iy = None
            try:
                iz = names.index(name[:-1] + "Z")
            except ValueError:
                iz = None
            if iy and iz:
                triple.append((name[:-1], ix, iy, iz))
                is_accounted_for[ix] = True
                is_accounted_for[iy] = True
                is_accounted_for[iz] = True
            else:
                single.append((name, ix))
                is_accounted_for[ix] = True
        elif name[-2:] == "_R":
            ir = k
            try:
                iz = names.index(name[:-2] + "_Z")
            except ValueError:
                iz = None
            if iz:
                double.append((name[:-2], ir, iz))
                is_accounted_for[ir] = True
                is_accounted_for[iz] = True
            else:
                single.append((name, ir))
                is_accounted_for[ir] = True
        else:
            single.append((name, k))
            is_accounted_for[k] = True

        k += 1

    if not all(is_accounted_for):
        raise ReadError()
    return single, double, triple


def read(file, timestep):

    with netCDF4.Dataset(file) as nc:
        # assert nc.version == np.float32(5.1)
        # assert nc.api_version == np.float32(5.1)
        # assert nc.floating_point_word_size == 8

        # assert b''.join(nc.variables['coor_names'][0]) == b'X'
        # assert b''.join(nc.variables['coor_names'][1]) == b'Y'
        # assert b''.join(nc.variables['coor_names'][2]) == b'Z'

        points = np.zeros((len(nc.dimensions["num_nodes"]), 3))
        point_data_names = []
        global_data_names = []
        cell_data_names = []
        pd = {}
        gd = []
        cd = {}
        cells = []
        ns_names = []
        # eb_names = []
        ns = []
        point_sets = {}
        info = []

        for key, value in nc.variables.items():
            if key == "info_records":
                value.set_auto_mask(False)
                for c in value[:]:
                    try:
                        info += [b"".join(c).decode("UTF-8")]
                    except UnicodeDecodeError:
                        # https://github.com/nschloe/meshio/issues/983
                        pass
            elif key == "qa_records":
                value.set_auto_mask(False)
                for val in value:
                    info += [b"".join(c).decode("UTF-8") for c in val[:]]
            elif key[:7] == "connect":
                meshio_type = exodus_to_meshio_type[value.elem_type.upper()]
                cells.append((meshio_type, value[:] - 1))
            elif key == "coord":
                points = nc.variables["coord"][:].T
            elif key == "coordx":
                points[:, 0] = value[:]
            elif key == "coordy":
                points[:, 1] = value[:]
            elif key == "coordz":
                points[:, 2] = value[:]
            elif key == "name_nod_var":
                value.set_auto_mask(False)
                point_data_names = [b"".join(c).decode("UTF-8") for c in value[:]]
            elif key[:12] == "vals_nod_var":
                idx = 0 if len(key) == 12 else int(key[12:]) - 1
                value.set_auto_mask(False)
                # For now only take the first value
                pd[idx] = value[timestep]
                # if len(value) > 1:
                # print("Skipping some time data")
            elif key == "name_glo_var":
                value.set_auto_mask(False)
                global_data_names = [b"".join(c).decode("UTF-8") for c in value[:]]
            elif key[:12] == "vals_glo_var":
                value.set_auto_mask(False)
                # For now only take the first value
                gd = value[timestep]
            elif key == "name_elem_var":
                value.set_auto_mask(False)
                cell_data_names = [b"".join(c).decode("UTF-8") for c in value[:]]
            elif key[:13] == "vals_elem_var":
                # eb: element block
                m = re.match("vals_elem_var(\\d+)?(?:eb(\\d+))?", key)
                idx = 0 if m.group(1) is None else int(m.group(1)) - 1
                block = 0 if m.group(2) is None else int(m.group(2)) - 1

                value.set_auto_mask(False)
                # For now only take the first value
                if idx not in cd:
                    cd[idx] = {}
                cd[idx][block] = value[timestep]

                # if len(value) > 1:
                # print("Skipping some time data")
            elif key == "ns_names":
                value.set_auto_mask(False)
                ns_names = [b"".join(c).decode("UTF-8") for c in value[:]]
            # elif key == "eb_names":
            #     value.set_auto_mask(False)
            #     eb_names = [b"".join(c).decode("UTF-8") for c in value[:]]
            elif key.startswith("node_ns"):  # Expected keys: node_ns1, node_ns2
                ns.append(value[:] - 1)  # Exodus is 1-based

        # merge element block data; can't handle blocks yet
        for k, value in cd.items():
            cd[k] = np.concatenate(list(value.values()))

        # Check if there are any <name>R, <name>Z tuples or <name>X, <name>Y, <name>Z
        # triplets in the point data. If yes, they belong together.
        single, double, triple = categorize(point_data_names)

        point_data = {}
        for name, idx in single:
            point_data[name] = pd[idx]
        for name, idx0, idx1 in double:
            point_data[name] = np.column_stack([pd[idx0], pd[idx1]])
        for name, idx0, idx1, idx2 in triple:
            point_data[name] = np.column_stack([pd[idx0], pd[idx1], pd[idx2]])

        single, double, triple = categorize(global_data_names)

        global_data = {}
        for name, idx in single:
            global_data[name] = gd[idx]
        for name, idx0, idx1 in double:
            global_data[name] = [gd[idx0], gd[idx1]]
        for name, idx0, idx1, idx2 in triple:
            global_data[name] = [gd[idx0], gd[idx1], gd[idx2]]

        cell_data = {}
        block_data = []
        k = 0
        for _, cell in cells:
            n = len(cell)
            block_data.append(cell)
            for name, data in zip(cell_data_names, cd.values()):
                if name not in cell_data:
                    cell_data[name] = []
                cell_data[name].append(data[k : k + n])
            k += n

        point_sets = {name: dat for name, dat in zip(ns_names, ns)}

    return points, point_data, global_data, cell_data, ns, block_data


P = 3780
a = 35.0
d = 0.00000023
w = 10
L = 37.1

# resultpath = "/home/jt/perihub/api/app/Output/CompactTension/CompactTension_Output1.e"
# resultpath = "/mnt/c/Users/hess_ja/Desktop/DockerProjects/periHubVolumes/peridigmJobs/dev/CompactTension/CompactTension_Output1.e"
resultpath = "/home/jt/perihub/api/app/Output/GIICmodel/GIICmodel_Output1.e"

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

for i in range(24, 25):
    points, point_data, global_data, cell_data, ns, block_data = read(resultpath, -1)
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
    P = global_data["Crosshead_Force"][1]
    d = global_data["Crosshead_Displacement"][0]
    GIIC = (9 * P * math.pow(a, 2) * d * 1000) / (
        2 * w * (1 / 4 * math.pow(L, 3) + 3 * math.pow(a, 3))
    )
    print(GIIC)

# idx = 0
# crack_acceleration = [0]
# delta_k1 = [0]
# delta_load = [0]
# for idx in range(0, len(Crack_length)):
#     if idx != 0:
#         crack_acceleration.append(Crack_length[idx] - Crack_length[idx - 1])
#         delta_k1.append(K1[idx] - K1[idx - 1])
#         delta_load.append(Load[idx] - Load[idx - 1])


plt.plot(Load, Crack_length)
plt.show
# plt.plot(range(0, len(Crack_length)), crack_acceleration)
# plt.plot(range(0, len(Crack_length)), Crack_length)
# plt.plot(delta_k1, crack_acceleration)
# plt.plot(range(0, len(Crack_length)), Load)
# plt.show
