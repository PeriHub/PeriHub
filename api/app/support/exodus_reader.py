import numpy as np
import re
import netCDF4


class ExodusReader:
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

    def read_timestep(file, timestep):

        with netCDF4.Dataset(file) as nc:
            # assert nc.version == np.float32(5.1)
            # assert nc.api_version == np.float32(5.1)
            # assert nc.floating_point_word_size == 8

            # assert b''.join(nc.variables['coor_names'][0]) == b'X'
            # assert b''.join(nc.variables['coor_names'][1]) == b'Y'
            # assert b''.join(nc.variables['coor_names'][2]) == b'Z'

            points = np.zeros((len(nc.dimensions["num_nodes"]), 3))
            time = 0.0
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
                    meshio_type = ExodusReader.exodus_to_meshio_type[
                        value.elem_type.upper()
                    ]
                    cells.append((meshio_type, value[:] - 1))
                elif key == "time_whole":
                    time = value[timestep]
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
            # for k, value in cd.items():
                # cd[k] = np.concatenate(list(value.values()))

            # Check if there are any <name>R, <name>Z tuples or <name>X, <name>Y, <name>Z
            # triplets in the point data. If yes, they belong together.
            single, double, triple = ExodusReader.categorize(point_data_names)

            point_data = {}
            for name, idx in single:
                point_data[name] = pd[idx]
            for name, idx0, idx1 in double:
                point_data[name] = np.column_stack([pd[idx0], pd[idx1]])
            for name, idx0, idx1, idx2 in triple:
                point_data[name] = np.column_stack([pd[idx0], pd[idx1], pd[idx2]])

            single, double, triple = ExodusReader.categorize(global_data_names)

            global_data = {}
            for name, idx in single:
                global_data[name] = gd[idx]
            for name, idx0, idx1 in double:
                global_data[name] = np.column_stack([gd[idx0], gd[idx1]])
            for name, idx0, idx1, idx2 in triple:
                global_data[name] = np.column_stack([gd[idx0], gd[idx1], gd[idx2]])

            cell_data = {}
            block_data = []
            k = 0
            for _, cell in cells:
                n = len(cell)
                block_data.append(cell)
            for name, data in zip(cell_data_names, cd.values()):
                if name not in cell_data:
                    cell_data[name] = []
                # cell_data[name].append(data[k : k + n])
                cell_data[name].append(data)
                k += n

            point_sets = {name: dat for name, dat in zip(ns_names, ns)}

        return points, point_data, global_data, cell_data, ns, block_data, time

    def read(file):

        with netCDF4.Dataset(file) as nc:

            points = np.zeros((len(nc.dimensions["num_nodes"]), 3))
            time = []
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
                    meshio_type = ExodusReader.exodus_to_meshio_type[
                        value.elem_type.upper()
                    ]
                    cells.append((meshio_type, value[:] - 1))
                elif key == "time_whole":
                    time = value[:]
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
                    pd[idx] = value[:]
                    # if len(value) > 1:
                    # print("Skipping some time data")
                elif key == "name_glo_var":
                    value.set_auto_mask(False)
                    global_data_names = [b"".join(c).decode("UTF-8") for c in value[:]]
                elif key[:12] == "vals_glo_var":
                    value.set_auto_mask(False)
                    # For now only take the first value
                    gd = value[:,:]
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
                    cd[idx][block] = value[:]

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
            # for k, value in cd.items():
                # cd[k] = np.concatenate(list(value.values()))

            # Check if there are any <name>R, <name>Z tuples or <name>X, <name>Y, <name>Z
            # triplets in the point data. If yes, they belong together.
            single, double, triple = ExodusReader.categorize(point_data_names)

            point_data = {}
            for name, idx in single:
                point_data[name] = []
                for sub_idx, _ in enumerate(pd[idx]):
                    point_data[name].append(pd[idx][sub_idx])
            for name, idx0, idx1 in double:
                point_data[name] = []
                for sub_idx, _ in enumerate(pd[idx0]):
                    point_data[name].append([pd[idx0][sub_idx], pd[idx1][sub_idx]])
            for name, idx0, idx1, idx2 in triple:
                point_data[name] = []
                for sub_idx, _ in enumerate(pd[idx0]):
                    point_data[name].append([pd[idx0][sub_idx], pd[idx1][sub_idx], pd[idx2][sub_idx]])

            single, double, triple = ExodusReader.categorize(global_data_names)

            global_data = {}
            for name, idx in single:
                global_data[name] = gd[:,idx]
            for name, idx0, idx1 in double:
                global_data[name] = np.column_stack([gd[:,idx0], gd[:,idx1]])
            for name, idx0, idx1, idx2 in triple:
                global_data[name] = np.column_stack([gd[:,idx0], gd[:,idx1], gd[:,idx2]])

            cell_data = {}
            block_data = []
            k = 0
            for _, cell in cells:
                n = len(cell)
                block_data.append(cell)
            for name, data in zip(cell_data_names, cd.values()):
                if name not in cell_data:
                    cell_data[name] = []
                # cell_data[name].append(data[k : k + n])
                cell_data[name].append(data)
                k += n

            point_sets = {name: dat for name, dat in zip(ns_names, ns)}

        return points, point_data, global_data, cell_data, ns, block_data, time

    def get_number_of_steps(file):

        with netCDF4.Dataset(file) as nc:

            time = []

            for key, value in nc.variables.items():
                if key == "time_whole":
                    time = value[:]

        return len(time) - 1
