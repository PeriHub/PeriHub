import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from support.base_models import Model
from support.exodus_reader import ExodusReader
from support.analysis import Analysis

class ImageExport:
    @staticmethod
    def numpy_line_plot(x,y):
        plt.title("Matplotlib demo") 
        plt.xlabel("x axis caption") 
        plt.ylabel("y axis caption") 
        plt.plot(x,y) 
        plt.show()
        return
        
    @staticmethod
    def get_result_image_from_exodus(file, displ_factor, marker_size, variable, axis, length, height):

        # resultpath = "./Results/" + os.path.join(username, model_name)
        # file = os.path.join(resultpath, model_name + "_" + output + ".e")

        # first_points, first_point_data, first_global_data, first_cell_data, first_ns, first_block_data, time = ExodusReader.read_timestep(
        #     file, 1
        # )
        points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(
            file, -1
        )

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
            min_value = min(cell_data[variable][0])
            max_value = max(cell_data[variable][0])
            for block_id in range(0,len(block_data)):
                if len(cell_data[variable][block_id])>0:
                    if min(cell_data[variable][block_id]) < min_value:
                        min_value = min(cell_data[variable][block_id])
                    if max(cell_data[variable][block_id]) < max_value:
                        max_value = max(cell_data[variable][block_id])
            for block_id in range(0,len(block_data)):

                block_ids = block_data[block_id][:, 0]

                block_points = points[block_ids]

                np_first_points_x = np.array(block_points[:, 0])
                np_first_points_y = np.array(block_points[:, 1])
                np_displacement_x = np.array(point_data['Displacement'][block_ids,0])
                np_displacement_y = np.array(point_data['Displacement'][block_ids,1])

                np_points_x = np.add(np_first_points_x, np.multiply(np_displacement_x, displ_factor))
                np_points_y = np.add(np_first_points_y, np.multiply(np_displacement_y, displ_factor))
                
                if len(cell_data[variable][block_id])>0:
                    scatter = ax.scatter(np_points_x, np_points_y, c=cell_data[variable][block_id], cmap=cm.jet, s=marker_size, vmin=min_value, vmax=max_value)
                else:
                    scatter = ax.scatter(np_points_x, np_points_y, cmap=cm.jet, s=marker_size)

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
        
        filepath = ''
        if 'Partial_Stress' in variable:
            filepath = file[:-2] + '_' + variable[:-1] + '_' + axis + '.png'
            fig.savefig(filepath, dpi=400)
        else:
            filepath = file[:-2] + '_' + variable + '_' + axis + '.png'
            fig.savefig(filepath, dpi=400)

        # plt.colorbar()
        plt.show()

        return filepath


    @staticmethod
    def get_plot_image_from_exodus(file, x_variable, x_axis, y_variable, y_axis):

        x_data = Analysis.get_global_data(file, x_variable, x_axis)
        y_data = Analysis.get_global_data(file, y_variable, y_axis)

        fig, ax = plt.subplots()

        ax.plot(x_data,y_data)
        ax.set_xlabel(x_variable)
        ax.set_ylabel(y_variable)

        fig.set_size_inches(18.5, 18.5)
        
        filepath = file[:-2] + '_' + x_variable + '_' + x_axis + '_' + y_variable + '_' + y_axis +'.png'
        fig.savefig(filepath, dpi=400)

        # plt.colorbar()
        plt.show()

        return filepath