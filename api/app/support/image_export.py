import os

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from exodusreader.exodusreader import ExodusReader
from fastapi import HTTPException, status
from mpl_toolkits.axes_grid1 import make_axes_locatable

from support.analysis import Analysis
from support.base_models import Model
from support.globals import log


class ImageExport:
    @staticmethod
    def long_edges(x, y, triangles, radio=0.75):
        out = []
        for points in triangles:
            # print points
            a, b, c = points
            d0 = np.sqrt((x[a] - x[b]) ** 2 + (y[a] - y[b]) ** 2)
            d1 = np.sqrt((x[b] - x[c]) ** 2 + (y[b] - y[c]) ** 2)
            d2 = np.sqrt((x[c] - x[a]) ** 2 + (y[c] - y[a]) ** 2)
            max_edge = max([d0, d1, d2])
            # print points, max_edge
            if max_edge > radio:
                out.append(True)
            else:
                out.append(False)
        return out

    @staticmethod
    def numpy_line_plot(x, y):
        plt.title("Matplotlib demo")
        plt.xlabel("x axis caption")
        plt.ylabel("y axis caption")
        plt.plot(x, y)
        plt.show()
        return

    @staticmethod
    def get_result_image_from_exodus(
        file,
        displ_factor,
        marker_size,
        variable,
        axis,
        length,
        height,
        triangulate,
        dx_value,
        step,
        cb_left,
        transparent,
        three_d,
        elevation,
        azimuth,
        roll,
    ):
        # resultpath = "./Results/" + os.path.join(username, model_name)
        # file = os.path.join(resultpath, model_name + "_" + output + ".e")

        # first_points, first_point_data, first_global_data, first_cell_data, first_ns, first_block_data, time = ExodusReader.read_timestep(
        #     file, 1
        # )
        Reader = ExodusReader()

        try:
            (
                points,
                point_data,
                global_data,
                cell_data,
                ns,
                block_data,
                time,
            ) = Reader.read_timestep(file, step)
        except IndexError:
            number_of_steps = Reader.get_number_of_steps(file)
            log.warning("Step can't be found, last step " + str(number_of_steps) + " used!")
            (
                points,
                point_data,
                global_data,
                cell_data,
                ns,
                block_data,
                time,
            ) = Reader.read_timestep(file, number_of_steps)

        use_cell_data = False

        if variable in [
            "Damage",
            "Partial_StressX",
            "Partial_StressY",
            "Partial_StressZ",
            "Number_Of_Neighbors",
            "Block",
        ]:
            use_cell_data = True

        axis_id = 0

        if axis == "X":
            axis_id = 0
            if "Partial_Stress" in variable:
                variable = variable + "X"
        elif axis == "Y":
            axis_id = 1
            if "Partial_Stress" in variable:
                variable = variable + "Y"
        elif axis == "Z":
            axis_id = 2
            if "Partial_Stress" in variable:
                variable = variable + "Z"
        elif axis == "Magnitude":
            axis_id = 0

        if three_d:
            fig = plt.figure(figsize=(22, 17))
            ax = fig.add_subplot(111, projection="3d")
            ax.view_init(elev=elevation, azim=azimuth, roll=roll)
        else:
            fig = plt.figure(figsize=(20, 20 * (height / length)))
            ax = fig.add_subplot(111)

        plt.rcParams.update({"font.size": 22})
        # I like to position my colorbars this way, but you don't have to
        # div = make_axes_locatable(ax)
        # if cb_left:
        #     cax = div.append_axes("left", "5%", "10%")
        # else:
        #     cax = div.append_axes("right", "5%", "5%")

        if use_cell_data:
            np_points_all_x = np.array([])
            np_points_all_y = np.array([])
            np_points_all_z = np.array([])

            cell_value = np.array([])

            for block_id in range(0, len(block_data)):
                block_ids = block_data[block_id][:, 0]

                block_points = points[block_ids]

                np_first_points_x = np.array(block_points[:, 0])
                np_first_points_y = np.array(block_points[:, 1])
                np_first_points_z = np.array(block_points[:, 2])

                if "Displacement" in point_data:
                    np_displacement_x = np.array(point_data["Displacement"][block_ids, 0])
                    np_displacement_y = np.array(point_data["Displacement"][block_ids, 1])
                    np_displacement_z = np.array(point_data["Displacement"][block_ids, 2])

                    np_points_x = np.add(
                        np_first_points_x,
                        np.multiply(np_displacement_x, displ_factor),
                    )
                    np_points_y = np.add(
                        np_first_points_y,
                        np.multiply(np_displacement_y, displ_factor),
                    )
                    np_points_z = np.add(
                        np_first_points_z,
                        np.multiply(np_displacement_z, displ_factor),
                    )
                else:
                    np_points_x = np_first_points_x
                    np_points_y = np_first_points_y
                    np_points_z = np_first_points_z

                np_points_all_x = np.concatenate([np_points_all_x, np_points_x])
                np_points_all_y = np.concatenate([np_points_all_y, np_points_y])
                np_points_all_z = np.concatenate([np_points_all_z, np_points_z])

                if variable == "Block":
                    cell_value = np.concatenate(
                        [
                            cell_value,
                            np.full_like(np_points_x, block_id),
                        ]
                    )
                else:
                    if block_id in cell_data[variable][0] and max(cell_data[variable][0][block_id]) > 0:
                        cell_value = np.concatenate(
                            [
                                cell_value,
                                cell_data[variable][0][block_id],
                            ]
                        )
                    else:
                        cell_value = np.concatenate([cell_value, np.full_like(np_points_x, 0)])

            if triangulate:
                try:
                    triang = mtri.Triangulation(np_points_all_x, np_points_all_y)

                except RuntimeError:
                    print("Failed to triangulate, displ_factor set to zero!")

                    np_points_all_x = np.array([])
                    np_points_all_y = np.array([])

                    for block_id in range(0, len(block_data)):
                        block_ids = block_data[block_id][:, 0]

                        block_points = points[block_ids]

                        np_first_points_x = np.array(block_points[:, 0])
                        np_first_points_y = np.array(block_points[:, 1])

                        np_points_all_x = np.concatenate([np_points_all_x, np_first_points_x])
                        np_points_all_y = np.concatenate([np_points_all_y, np_first_points_y])

                    triang = mtri.Triangulation(np_points_all_x, np_points_all_y)
                try:
                    mask = ImageExport.long_edges(
                        np_points_all_x,
                        np_points_all_y,
                        triang.triangles,
                        dx_value,
                    )
                    triang.set_mask(mask)

                    # plt.triplot(triang)
                    tcf = ax.tricontourf(triang, cell_value, levels=100, cmap=cm.jet)
                except ValueError:
                    log.error("Failed to triangulate, dx_value to small")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to triangulate, dx_value to small",
                    )

                cbar = fig.colorbar(tcf)

            else:
                if three_d:
                    scatter = ax.scatter(
                        np_points_all_x,
                        np_points_all_y,
                        np_points_all_z,
                        c=cell_value,
                        cmap=cm.jet,
                        s=marker_size,
                    )
                else:
                    scatter = ax.scatter(
                        np_points_all_x,
                        np_points_all_y,
                        c=cell_value,
                        cmap=cm.jet,
                        s=marker_size,
                    )

                cbar = fig.colorbar(scatter)

        else:
            np_first_points_x = np.array(points[:, 0])
            np_first_points_y = np.array(points[:, 1])
            np_first_points_z = np.array(points[:, 2])

            try:
                np_displacement_x = np.array(point_data["Displacement"][:, 0])
                np_displacement_y = np.array(point_data["Displacement"][:, 1])
                np_displacement_z = np.array(point_data["Displacement"][:, 2])

                np_points_x = np.add(
                    np_first_points_x,
                    np.multiply(np_displacement_x, displ_factor),
                )
                np_points_y = np.add(
                    np_first_points_y,
                    np.multiply(np_displacement_y, displ_factor),
                )
                np_points_z = np.add(
                    np_first_points_z,
                    np.multiply(np_displacement_z, displ_factor),
                )

            except:
                np_points_x = np_first_points_x
                np_points_y = np_first_points_y
                np_points_z = np_first_points_z

            if triangulate:
                try:
                    triang = mtri.Triangulation(np_points_x, np_points_y)
                except RuntimeError:
                    print("Failed to triangulate, displ_factor set to zero!")

                    np_first_points_x = np.array(points[:, 0])
                    np_first_points_y = np.array(points[:, 1])
                    triang = mtri.Triangulation(np_first_points_x, np_first_points_y)

                try:
                    mask = ImageExport.long_edges(np_points_x, np_points_y, triang.triangles, dx_value)
                    triang.set_mask(mask)

                    tcf = ax.tricontourf(
                        triang,
                        point_data[variable][:, axis_id],
                        levels=100,
                        cmap=cm.jet,
                    )
                except ValueError:
                    log.error("Failed to triangulate, dx_value to small")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to triangulate, dx_value to small",
                    )

                cbar = fig.colorbar(tcf)

            else:
                cell_value = []
                if variable == "Temperature":
                    cell_value = point_data[variable]
                else:
                    cell_value = point_data[variable][:, axis_id]

                if three_d:
                    scatter = ax.scatter(
                        np_points_x,
                        np_points_y,
                        np_points_z,
                        c=cell_value,
                        cmap=cm.jet,
                        s=marker_size,
                    )
                else:
                    scatter = ax.scatter(
                        np_points_x,
                        np_points_y,
                        c=cell_value,
                        cmap=cm.jet,
                        s=marker_size,
                    )

                cbar = fig.colorbar(scatter)

        ax.set_title("Time: " + "{:.6f}".format(time))

        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0
        # set colorbar label plus label color
        if use_cell_data:
            cbar.set_label(variable, color="black")
            x_min = np.min(np_points_all_x)
            x_max = np.max(np_points_all_x)
            y_min = np.min(np_points_all_y)
            y_max = np.max(np_points_all_y)
        else:
            cbar.set_label(variable + "_" + axis, color="black")
            x_min = np.min(np_points_x)
            x_max = np.max(np_points_x)
            y_min = np.min(np_points_y)
            y_max = np.max(np_points_y)

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # set colorbar tick color
        cbar.ax.yaxis.set_tick_params(color="black")

        # set colorbar edgecolor
        cbar.outline.set_edgecolor("black")

        filepath = ""
        if use_cell_data:
            if "Partial_Stress" in variable:
                filepath = file[:-2] + "_" + variable[:-1] + "_" + axis + ".png"
            else:
                filepath = file[:-2] + "_" + variable + ".png"
        else:
            filepath = file[:-2] + "_" + variable + "_" + axis + ".png"

        fig.savefig(filepath, dpi=400, transparent=transparent)

        # plt.colorbar()
        plt.show()

        return filepath

    @staticmethod
    def get_plot_image_from_exodus(file, x_variable, x_axis, y_variable, y_axis):
        x_data = Analysis.get_global_data(file, x_variable, x_axis)
        y_data = Analysis.get_global_data(file, y_variable, y_axis)

        fig, ax = plt.subplots()

        ax.plot(x_data, y_data)
        ax.set_xlabel(x_variable)
        ax.set_ylabel(y_variable)

        fig.set_size_inches(18.5, 18.5)

        filepath = file[:-2] + "_" + x_variable + "_" + x_axis + "_" + y_variable + "_" + y_axis + ".png"
        fig.savefig(filepath, dpi=400)

        # plt.colorbar()
        plt.show()

        return filepath
