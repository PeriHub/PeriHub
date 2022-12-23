
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.tri as mtri
from mpl_toolkits.axes_grid1 import make_axes_locatable
from exodusreader.exodusreader import ExodusReader

@staticmethod
def long_edges(x, y, triangles, radio=0.75):
    out = []
    for points in triangles:
        #print points
        a,b,c = points
        d0 = np.sqrt( (x[a] - x[b]) **2 + (y[a] - y[b])**2 )
        d1 = np.sqrt( (x[b] - x[c]) **2 + (y[b] - y[c])**2 )
        d2 = np.sqrt( (x[c] - x[a]) **2 + (y[c] - y[a])**2 )
        max_edge = max([d0, d1, d2])
        #print points, max_edge
        if max_edge > radio:
            out.append(True)
        else:
            out.append(False)
    return out

file1 = "/mnt/c/Users/hess_ja/Desktop/GcodeResults/var_2/LShape.e"
file2 = "/mnt/c/Users/hess_ja/Desktop/GcodeResults/var_3/LShape.e"

variable= "Temperature"
axis = "x"
step = 440
height =  0.05
length =  0.05
triangulate = True
dx_value = 0.00025
cb_left = False
displ_factor = 1
marker_size = 0.01
transparent = False

reader = ExodusReader()

try:
    points1, point_data1, global_data1, cell_data1, ns1, block_data1, time1 = reader.read_timestep(file1, step)
    points2, point_data2, global_data2, cell_data2, ns2, block_data2, time2 = reader.read_timestep(file2, step)
except IndexError:
    number_of_steps1 = ExodusReader.get_number_of_steps(file1)
    print("Step can't be found, last step " + str(number_of_steps1) + " used!")
    points1, point_data1, global_data1, cell_data1, ns1, block_data1, time1 = reader.read_timestep(file1, number_of_steps1)
    points2, point_data2, global_data2, cell_data2, ns2, block_data2, time2 = reader.read_timestep(file2, number_of_steps1)

use_cell_data=False

if variable in ['Damage','Partial_StressX','Partial_StressY','Partial_StressZ', 'Number_Of_Neighbors', 'Block']:
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

fig = plt.figure(figsize=(20, 20*(height/length)))
ax = fig.add_subplot(111)

# I like to position my colorbars this way, but you don't have to
div = make_axes_locatable(ax)
if cb_left:
    cax = div.append_axes('left', '5%', '10%')
else:
    cax = div.append_axes('right', '5%', '5%')

if use_cell_data:
            
    np_points_all_x = np.array([])
    np_points_all_y = np.array([])

    cell_value = np.array([])

    for block_id in range(0,len(block_data)):

        block_ids = block_data[block_id][:, 0]

        block_points = points[block_ids]

        np_first_points_x = np.array(block_points[:, 0])
        np_first_points_y = np.array(block_points[:, 1])
        np_displacement_x = np.array(point_data['Displacement'][block_ids,0])
        np_displacement_y = np.array(point_data['Displacement'][block_ids,1])

        np_points_x = np.add(np_first_points_x, np.multiply(np_displacement_x, displ_factor))
        np_points_y = np.add(np_first_points_y, np.multiply(np_displacement_y, displ_factor))
        
        np_points_all_x = np.concatenate([np_points_all_x,np_points_x])
        np_points_all_y = np.concatenate([np_points_all_y,np_points_y])

        if variable == 'Block':
            cell_value = np.concatenate([cell_value, np.full_like(np_points_x,block_id)])
        else:
            if block_id in cell_data[variable][0] and max(cell_data[variable][0][block_id]) > 0:
                cell_value = np.concatenate([cell_value, cell_data[variable][0][block_id]])
            else:
                cell_value = np.concatenate([cell_value, np.full_like(np_points_x,0)])

    if triangulate:

        try:
            triang = mtri.Triangulation(np_points_all_x, np_points_all_y)

        except RuntimeError:
            print("Failed to triangulate, displ_factor set to zero!")

            np_points_all_x = np.array([])
            np_points_all_y = np.array([])

            for block_id in range(0,len(block_data)):

                block_ids = block_data[block_id][:, 0]

                block_points = points[block_ids]

                np_first_points_x = np.array(block_points[:, 0])
                np_first_points_y = np.array(block_points[:, 1])
                
                np_points_all_x = np.concatenate([np_points_all_x,np_first_points_x])
                np_points_all_y = np.concatenate([np_points_all_y,np_first_points_y])

            triang = mtri.Triangulation(np_points_all_x, np_points_all_y)
            
        mask = ImageExport.long_edges(np_points_all_x, np_points_all_y, triang.triangles, dx_value)
        triang.set_mask(mask)
    
        # plt.triplot(triang)
        tcf = ax.tricontourf(triang, cell_value, levels=100, cmap=cm.jet)
        
        cbar = fig.colorbar(tcf, cax=cax)

    else:

        scatter = ax.scatter(np_points_all_x, np_points_all_y, c=cell_value, cmap=cm.jet, s=marker_size)

        cbar = fig.colorbar(scatter, cax=cax)

else:
    np_points_x = np.array(points1[:, 0])
    np_points_y = np.array(points1[:, 1])

    point_data_diff = np.subtract(np.array(point_data1[variable]),np.array(point_data2[variable]))

    if triangulate:
    
        try:
            triang = mtri.Triangulation(np_points_x, np_points_y)
        except RuntimeError:
            print("Failed to triangulate, displ_factor set to zero!")

            np_first_points_x = np.array(points1[:, 0])
            np_first_points_y = np.array(points1[:, 1])
            triang = mtri.Triangulation(np_first_points_x, np_first_points_y)

        mask = long_edges(np_points_x, np_points_y, triang.triangles, dx_value)
        triang.set_mask(mask)

        tcf = ax.tricontourf(triang, point_data_diff, levels=100, cmap=cm.jet)
        
        cbar = fig.colorbar(tcf, cax=cax)

    else:

        scatter = ax.scatter(np_points_x, np_points_y, c=point_data_diff, cmap=cm.jet, s=marker_size)

        cbar = fig.colorbar(scatter, cax=cax)

ax.set_title('Time: ' + "{:.6f}".format(time1))

x_min=0
x_max=0
y_min=0
y_max=0
# set colorbar label plus label color
if use_cell_data:
    cbar.set_label(variable, color='black')
    x_min=np.min(np_points_all_x)
    x_max=np.max(np_points_all_x)
    y_min=np.min(np_points_all_y)
    y_max=np.max(np_points_all_y)
else:
    cbar.set_label(variable + '_' + axis, color='black')
    x_min=np.min(np_points_x)
    x_max=np.max(np_points_x)
    y_min=np.min(np_points_y)
    y_max=np.max(np_points_y)

ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

# set colorbar tick color
cbar.ax.yaxis.set_tick_params(color='black')

# set colorbar edgecolor 
cbar.outline.set_edgecolor('black')

filepath = ''
if use_cell_data:
    if 'Partial_Stress' in variable:
        filepath = file1[:-2] + '_' + variable[:-1] + '_' + axis + '.png'
    else:
        filepath = file1[:-2] + '_' + variable + '.png'
else:
    filepath = file1[:-2] + '_' + variable + '_' + axis + '.png'

fig.savefig(filepath, dpi=400, transparent=transparent)

# plt.colorbar()
plt.show()

# return filepath