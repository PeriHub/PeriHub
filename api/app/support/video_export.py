import matplotlib.animation as animation
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from exodusreader.exodusreader import ExodusReader
from mpl_toolkits.axes_grid1 import make_axes_locatable


class VideoExport:
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
    def get_gif_from_exodus(
        file,
        apply_displacements,
        displ_factor,
        max_edge_distance,
        variable,
        axis,
        length,
        height,
        fps,
        dpi,
        x_min,
        x_max,
        y_min,
        y_max,
        size=20,
    ):
        Reader = ExodusReader()

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = Reader.read(file)

        use_cell_data = False

        if variable in [
            "Damage",
            "Partial_StressX",
            "Partial_StressY",
            "Partial_StressZ",
            "Number_Of_Neighbors",
        ]:
            use_cell_data = True

        axis_id = 0

        if axis == "x":
            axis_id = 0
            if "Partial_Stress" in variable:
                variable = variable + "X"
        elif axis == "y":
            axis_id = 1
            if "Partial_Stress" in variable:
                variable = variable + "Y"
        elif axis == "z":
            axis_id = 2
            if "Partial_Stress" in variable:
                variable = variable + "Z"
        elif axis == "Magnitude":
            axis_id = 0

        fig = plt.figure(figsize=(size, size * (height / length)))
        ax = fig.add_subplot(111)

        # I like to position my colorbars this way, but you don't have to
        div = make_axes_locatable(ax)
        cax = div.append_axes("right", "5%", "5%")

        v_min = 0
        v_max = 0

        if use_cell_data:
            for i in range(1, len(time)):
                for block_id in range(0, len(block_data)):
                    if block_id in cell_data[variable][0]:
                        min_value = min(cell_data[variable][0][block_id][i])
                        max_value = max(cell_data[variable][0][block_id][i])
                        if min_value < v_min:
                            v_min = min_value
                        if max_value > v_max:
                            v_max = max_value

            print(v_min)
            print(v_max)

            np_points_x = np.array([])
            np_points_y = np.array([])

            cell_value = np.array([])

            for block_id in range(0, len(block_data)):
                block_ids = block_data[block_id][:, 0]

                block_points = points[block_ids]

                np_first_points_x = np.array(block_points[:, 0])
                np_first_points_y = np.array(block_points[:, 1])
                np_points_x = np.concatenate([np_points_x, np_first_points_x])
                np_points_y = np.concatenate([np_points_y, np_first_points_y])

                if block_id in cell_data[variable][0] and max(cell_data[variable][-1][block_id][0]) > 0:
                    cell_value = np.concatenate(
                        [
                            cell_value,
                            cell_data[variable][-1][block_id][0],
                        ]
                    )
                else:
                    cell_value = np.concatenate([cell_value, np.full_like(np_first_points_x, 0)])

            triang = mtri.Triangulation(np_points_x, np_points_y)
            mask = VideoExport.long_edges(
                np_points_x,
                np_points_y,
                triang.triangles,
                max_edge_distance,
            )
            triang.set_mask(mask)

            # plt.triplot(triang)
            tcf = ax.tricontourf(
                triang,
                cell_value,
                levels=100,
                cmap=cm.jet,
                vmin=v_min,
                vmax=v_max,
            )

            fig.colorbar(tcf, cax=cax)
            tx = ax.set_title("Frame 0")

            if apply_displacements and x_min:
                ax.set_xlim(x_min, x_max)
                ax.set_ylim(y_min, y_max)

            def animate(i, triang):
                ax.clear()
                if apply_displacements and x_min:
                    ax.set_xlim(x_min, x_max)
                    ax.set_ylim(y_min, y_max)

                print(i)

                if apply_displacements:
                    np_points_all_x = np.array([])
                    np_points_all_y = np.array([])

                cell_value = np.array([])
                for block_id in range(0, len(block_data)):
                    block_ids = block_data[block_id][:, 0]

                    if apply_displacements:
                        block_points = points[block_ids]

                        np_first_points_x = np.array(block_points[:, 0])
                        np_first_points_y = np.array(block_points[:, 1])
                        np_displacement_x = np.array(point_data["Displacement"][i][0][block_ids])
                        np_displacement_y = np.array(point_data["Displacement"][i][1][block_ids])

                        np_points_x = np.add(
                            np_first_points_x,
                            np.multiply(np_displacement_x, displ_factor),
                        )
                        np_points_y = np.add(
                            np_first_points_y,
                            np.multiply(np_displacement_y, displ_factor),
                        )

                        np_points_all_x = np.concatenate([np_points_all_x, np_points_x])
                        np_points_all_y = np.concatenate([np_points_all_y, np_points_y])

                    if block_id in cell_data[variable][0] and max(cell_data[variable][0][block_id][i]) > 0:
                        cell_value = np.concatenate(
                            [
                                cell_value,
                                cell_data[variable][0][block_id][i],
                            ]
                        )
                    else:
                        cell_value = np.concatenate([cell_value, np.full_like(block_ids, 0)])

                if apply_displacements:
                    triang = mtri.Triangulation(np_points_all_x, np_points_all_y)
                    print(len(np_points_all_x))
                    mask = VideoExport.long_edges(
                        np_points_all_x,
                        np_points_all_y,
                        triang.triangles,
                        max_edge_distance,
                    )
                    triang.set_mask(mask)

                tcf = ax.tricontourf(
                    triang,
                    cell_value,
                    levels=100,
                    cmap=cm.jet,
                    vmin=v_min,
                    vmax=v_max,
                )

                cax.cla()
                fig.colorbar(tcf, cax=cax)
                tx.set_text("Frame {0}".format(i))

            ani = animation.FuncAnimation(fig, animate, fargs=(triang,), frames=len(time))

        else:
            for i in range(1, len(time)):
                min_value = min(point_data[variable][i][0][:])
                max_value = max(point_data[variable][i][0][:])
                if min_value < v_min:
                    v_min = min_value
                if max_value > v_max:
                    v_max = max_value
            print(v_min)
            print(v_max)

            triang = mtri.Triangulation(points[:, 0], points[:, 1])
            mask = VideoExport.long_edges(
                points[:, 0],
                points[:, 1],
                triang.triangles,
                max_edge_distance,
            )
            triang.set_mask(mask)
            # plt.triplot(triang)

            tcf = ax.tricontourf(
                triang,
                point_data[variable][0][axis_id][:],
                levels=100,
                cmap=cm.jet,
                vmin=v_min,
                vmax=v_max,
            )

            fig.colorbar(tcf, cax=cax)
            tx = ax.set_title("Frame 0")

            def animate(i, triang):
                print("Frame " + str(i) + " of " + str(len(time)))
                tcf = ax.tricontourf(
                    triang,
                    point_data[variable][i][axis_id][:],
                    levels=100,
                    cmap=cm.jet,
                    vmin=v_min,
                    vmax=v_max,
                )
                cax.cla()
                fig.colorbar(tcf, cax=cax)
                tx.set_text("Frame {0}".format(i))

            ani = animation.FuncAnimation(fig, animate, fargs=(triang,), frames=len(time))

        filepath = file[:-2] + "_" + variable + "_" + axis + ".gif"

        ani.save(filepath, writer=animation.PillowWriter(fps=fps), dpi=dpi)

        plt.show()

        return filepath

    @staticmethod
    def get_triangulated_mesh_from_exodus(file, displ_factor, timestep, max_edge_distance, length, height):
        Reader = ExodusReader()

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = Reader.read_timestep(file, timestep)

        fig = plt.figure(figsize=(20, 20 * (height / length)))
        fig.add_subplot(111)

        np_first_points_x = np.array(points[:, 0])
        np_first_points_y = np.array(points[:, 1])
        np_displacement_x = np.array(point_data["Displacement"][:, 0])
        np_displacement_y = np.array(point_data["Displacement"][:, 1])

        np_points_x = np.add(
            np_first_points_x,
            np.multiply(np_displacement_x, displ_factor),
        )
        np_points_y = np.add(
            np_first_points_y,
            np.multiply(np_displacement_y, displ_factor),
        )

        triang = mtri.Triangulation(np_points_x, np_points_y)
        mask = VideoExport.long_edges(
            np_points_x,
            np_points_y,
            triang.triangles,
            max_edge_distance,
        )
        triang.set_mask(mask)

        plt.triplot(triang)

        filepath = file[:-2] + "_triang.png"

        fig.savefig(filepath)

        plt.show()

        return filepath
