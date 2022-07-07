import os
import math
import numpy as np
# import matplotlib.pyplot as plt

class GcodeReader:

    def mesh_file_writer(filepath, string, mesh_array, mesh_format):
        """doc"""
        print("Write mesh file")
        with open(filepath, "w", encoding="UTF-8") as file:
            file.write(string)
            np.savetxt(file, mesh_array, fmt=mesh_format, delimiter=" ")


    def write_mesh(model, filepath):
        """doc"""
        string = "# x y z block_id volume time\n"
        GcodeReader.mesh_file_writer(filepath + ".txt", string, model, "%.18e %.18e %.18e %d %.18e %.18e")


    @staticmethod
    def gcode_to_peridigm(filename, localpath, discretization):
        """doc"""
        # filename = "Box_100x30x50.gcode"
        # filename = "Design1_robert.gcode"
        # filename = "Test.gcode"

        filepath = os.path.join(localpath, filename)

        with open(filepath + '.gcode') as f:
            content = f.readlines()

        points = [0, 0, 0]
        ext1 = []
        ext2 = []
        feedrate = []
        nozzle = []

        max_feedrate = 6000

        point = [0, 0, 0]
        x = []
        y = []
        z = []
        fr = 0
        e1 = 0
        tool = 0

        for line in content:
            # print(line)
            parts = line.split(" ")

            done = False

            if parts[0] in ["G1", "G0"]:

                pointDef = False

                for part in parts[1:]:

                    if "\t" in part or len(part) == 0:
                        break
                    # tmp=float(part[1:])

                    if part[0] == "X":
                        point[0] = float(part[1:])
                    elif part[0] == "Y":
                        point[1] = float(part[1:])
                        pointDef = True
                    elif part[0] == "Z":
                        point[2] = float(part[1:])
                        # pointDef = True
                    elif part[0] == "E":
                        e1 = float(part[1:])
                    elif part[0] == "F":
                        fr = float(part[1:])

                    if "\n" in part and pointDef:
                        done = True
                        x.append(point[0])
                        y.append(point[1])
                        z.append(point[2])
                        ext1.append(e1)
                        feedrate.append(fr)
                        nozzle.append(tool)
                        # print(str(point[0])+" "+str(point[1])+" "+ str(point[2]))

                    if done:
                        break

            elif parts[0] == "T0":
                tool = 0
            elif parts[0] == "T1":
                tool = 1

        x_peri = []
        y_peri = []
        z_peri = []
        time = []

        volume = 1e-3

        k = []
        vol = []

        x0 = 0
        y0 = 0
        z0 = 0

        x1 = 0
        y1 = 0
        z1 = 0

        # dx_value = [0.1, 0.1, 0.1]
        dx_value = [discretization, discretization, discretization]

        for i in range(1, len(x)):

            # if feedrate[i] < max_feedrate:

            x0 = x[i - 1]
            y0 = y[i - 1]
            z0 = z[i - 1]

            x1 = x[i]
            y1 = y[i]
            z1 = z[i]

            # if feedrate[i - 1] == max_feedrate:

            #     x2 = x[i + 1]
            #     y2 = y[i + 1]
            #     z2 = z[i + 1]

            #     distance = math.sqrt(
            #         math.pow(x2 - x2, 2) + math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2)
            #     )
            #     # print(distance)
            #     if distance != 0.0:
            #         x_peri.append(x1)
            #         y_peri.append(y1)
            #         z_peri.append(z1)
            #         time_needed = distance / feedrate[i]
            #         if len(time) == 0:
            #             time.append(time_needed)
            #         else:
            #             time.append(time[-1] + time_needed)
            #         vol.append(volume * (dx_value[0] / distance))

            #     continue

            distance = math.sqrt(
                math.pow(x1 - x0, 2) + math.pow(y1 - y0, 2) + math.pow(z1 - z0, 2)
            )
            # print(str(distance))

            if distance != 0.0:

                time_needed = distance / feedrate[i]

                if distance > dx_value[0]:

                    x_range = []
                    y_range = []
                    z_range = []

                    dx_min = min(dx_value)

                    num_nodes = int(distance / dx_min)

                    # if x1 != x0:
                    #     if x1 >= x0:
                    #         x_range = np.arange(x0, x1, dx_value[0])
                    #     else:
                    #         x_range = np.arange(x1, x0, dx_value[0])
                    #     y_range = np.full_like(x_range, y1)
                    #     z_range = np.full_like(x_range, z1)

                    # if y1 != y0:
                    #     if y1 >= y0:
                    #         y_range = np.arange(y0, y1, dx_value[1])
                    #     else:
                    #         y_range = np.arange(y1, y0, dx_value[1])
                    #     x_range = np.full_like(y_range, x1)
                    #     z_range = np.full_like(y_range, z1)

                    # if z1 != z0:
                    #     if z1 >= z0:
                    #         z_range = np.arange(z0, z1, dx_value[2])
                    #     else:
                    #         z_range = np.arange(z1, z0, dx_value[2])
                    #     x_range = np.full_like(z_range, x1)
                    #     y_range = np.full_like(z_range, y1)

                    x_range = np.linspace(x0, x1, num=num_nodes, endpoint=False)
                    y_range = np.linspace(y0, y1, num=num_nodes, endpoint=False)
                    z_range = np.linspace(z0, z1, num=num_nodes, endpoint=False)

                    if len(time) != 0:
                        time_range = np.linspace(
                            time[-1], time[-1] + time_needed, num=len(x_range), endpoint=False
                        )
                    else:
                        time_range = np.linspace(
                            0, time_needed, num=len(x_range), endpoint=False
                        )

                    # test2=np.linspace(y0, y1, int(distance/dx_value[1])),
                    # test3=np.linspace(z0, z1, int(distance/dx_value[2])),

                    # gridx, gridy, gridz = np.meshgrid(
                    #             np.linspace(x0, x1, int(distance/dx_value[0])),
                    #             np.linspace(y0, y1, int(distance/dx_value[1])),
                    #             np.linspace(z0, z1, int(distance/dx_value[2])),
                    #         )

                    # gridx, gridy, gridz = np.meshgrid(
                    #     x_range,
                    #     y_range,
                    #     z_range,
                    # )

                    # grid_x_value = gridx[1:].ravel()
                    # grid_y_value = gridy[1:].ravel()
                    # grid_z_value = gridz[1:].ravel()

                    x_peri.extend(x_range)
                    y_peri.extend(y_range)
                    z_peri.extend(z_range)

                    time.extend(time_range)

                    vol.extend(np.full_like(x_range, volume))

                x_peri.append(x1)
                y_peri.append(y1)
                z_peri.append(z1)

                time.append(time[-1] + time_needed)

                vol.append(volume * (dx_value[0] / distance))

        # filter = np.full_like(x_peri, 1)

        # for i in range(0, len(x_peri) - 1):
        #     for j in range(i + 1, len(x_peri)):
        #         if x_peri[i] == x_peri[j] and y_peri[i] == y_peri[j] and z_peri[i] == z_peri[j]:
        #             filter[j] == 0

        # x_peri_np = np.array(x_peri)
        # y_peri_np = np.array(y_peri)
        # z_peri_np = np.array(z_peri)

        points_np = np.dstack((x_peri, y_peri, z_peri))
        filtered_points, indices = np.unique(points_np[0], axis=0, return_index=True)
        # print(points_np[0])
        x_peri_np = filtered_points[:, 0]
        y_peri_np = filtered_points[:, 1]
        z_peri_np = filtered_points[:, 2]
        vol_np = np.take(vol, indices)
        time_np = np.take(time, indices)

        k = np.full_like(x_peri_np, 1)
        # vol = np.full_like(x_peri_np, 1e-3)

        nodesets = [[0,300,-500,500,-500,2],[0,300,-500,-500,26,500]]

        for i, node in enumerate(nodesets):
            k = np.where(
                        np.logical_and(
                            np.logical_and(
                                np.logical_and(
                                    x_peri_np >= node[0],
                                    x_peri_np <= node[1],
                                ),
                                np.logical_and(
                                    y_peri_np >=  node[2],
                                    y_peri_np <=  node[3],
                                ),),
                            np.logical_and(
                                z_peri_np >=  node[4],
                                z_peri_np <=  node[5],
                            ),
                        ),
                        i+2,
                        k,
                    )

        model = np.transpose(
            np.vstack(
                [
                    x_peri_np.ravel(),
                    y_peri_np.ravel(),
                    z_peri_np.ravel(),
                    k.ravel(),
                    vol_np.ravel(),
                    time_np.ravel(),
                ]
            )
        )

        GcodeReader.write_mesh(model, filepath)


        # ns1 = open(r"ns_Test_1.txt", "w")
        # ns2 = open(r"ns_Test_2.txt", "w")

        myString = []

        for node in nodesets:
            myString.append("")

        idx = 1
        for x,y,z in filtered_points:
            for i, node in enumerate(nodesets):
                if x <= node[0] and x >= node[1]:
                    if y <= node[2] and y >= node[3]:
                        if z <= node[4] and z >= node[5]:
                            myString[i] += str(idx) + " \n"
            idx = idx + 1
        for idx, _ in enumerate(nodesets):
            ns = open(os.path.join(localpath,"ns_"+filename+"_"+ str(idx+1) +".txt"), "w")
            ns.write(myString[idx])
            ns.close()


        print("Finished")
