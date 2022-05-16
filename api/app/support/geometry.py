"""
doc
"""
import math
import time
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


class Geometry:
    @staticmethod
    def create_rectangle(coor, dx_value):
        """doc"""
        start_time = time.time()
        if coor[4] == coor[5]:
            gridx, gridy = np.meshgrid(
                np.arange(coor[0], coor[1] + dx_value[0], dx_value[0]),
                np.arange(coor[2], coor[3] + dx_value[1], dx_value[1]),
            )
            grid_x_value = gridx.ravel()
            grid_y_value = gridy.ravel()
            grid_z_value = 0 * gridy.ravel()
        else:
            gridx, gridy, gridz = np.meshgrid(
                np.arange(coor[0], coor[1] + dx_value[0], dx_value[0]),
                np.arange(coor[2], coor[3] + dx_value[1], dx_value[1]),
                np.arange(coor[4], coor[5] + dx_value[2], dx_value[2]),
            )
            grid_x_value = gridx.ravel()
            grid_y_value = gridy.ravel()
            grid_z_value = gridz.ravel()

        print(f"Points created  in {(time.time() - start_time):.2f} seconds")
        return grid_x_value, grid_y_value, grid_z_value

    @staticmethod
    def create_cylinder(coor, dx_value, radius):
        """doc"""
        start_time = time.time()

        gridx = [coor[0]]
        gridy = [coor[1]]
        gridz = [coor[2]]

        max_number_of_nodes = (2 * np.pi * radius) / dx_value[0]
        max_number_of_nodes = 2 * int(max_number_of_nodes / 2) + 1

        number_of_circles = int(radius / dx_value[1])

        for i in range(0, number_of_circles):
            number_of_nodes = int(max_number_of_nodes * (i + 1) / number_of_circles)
            theta = np.linspace(0, 2 * np.pi, number_of_nodes)

            gridx.extend(
                coor[0] + radius * (i + 1) / number_of_circles * np.cos(theta[:-1])
            )
            gridy.extend(
                coor[1] + radius * (i + 1) / number_of_circles * np.sin(theta[:-1])
            )
            gridz.extend(0 * theta[:-1])

        # plt.scatter(gridx, gridy)
        # plt.show()

        if coor[2] == 0:

            grid_x_value = np.array(gridx).ravel()
            grid_y_value = np.array(gridy).ravel()
            grid_z_value = np.array(gridz).ravel()

        else:
            gridx_3d = []
            gridy_3d = []
            gridz_3d = []

            for z in np.arange(0, coor[2] + dx_value[2], dx_value[2]):
                gridx_3d.extend(gridx)
                gridy_3d.extend(gridy)
                gridz_3d.extend(np.full_like(gridx, z))

            grid_x_value = np.array(gridx_3d).ravel()
            grid_y_value = np.array(gridy_3d).ravel()
            grid_z_value = np.array(gridz_3d).ravel()

        # if length == 0:
        #     gridx, gridy = np.meshgrid(
        #         np.arange(
        #             coor[0] - radius, coor[0] + radius + dx_value[0], dx_value[0]
        #         ),
        #         np.arange(
        #             coor[1] - radius, coor[1] + radius + dx_value[1], dx_value[1]
        #         ),
        #     )
        #     grid_x_value = gridx.ravel()
        #     grid_y_value = gridy.ravel()
        #     grid_z_value = 0 * gridy.ravel()
        # else:
        #     gridx, gridy, gridz = np.meshgrid(
        #         np.arange(
        #             coor[0] - radius, coor[0] + radius + dx_value[0], dx_value[0]
        #         ),
        #         np.arange(
        #             coor[1] - radius, coor[1] + radius + dx_value[1], dx_value[1]
        #         ),
        #         np.arange(coor[2] - length / 2, coor[2] + length / 2, dx_value[2]),
        #     )
        #     grid_x_value = gridx.ravel()
        #     grid_y_value = gridy.ravel()
        #     grid_z_value = gridz.ravel()

        # grid_x_value, grid_y_value, grid_z_value = Geometry.check_val_in_circle(
        #     grid_x_value, grid_y_value, grid_z_value, coor[0], coor[1], radius, True
        # )

        print(f"Points created  in {(time.time() - start_time):.2f} seconds")
        return grid_x_value, grid_y_value, grid_z_value

    @staticmethod
    def check_val_in_circle(
        array_x, array_y, array_z, origin_x, origin_y, radius, in_circle
    ):
        """doc"""
        if in_circle:
            condition = np.where(
                np.sqrt(
                    np.power(array_x - origin_x, 2) + np.power(array_y - origin_y, 2)
                )
                <= radius,
                1.0,
                0,
            )
        else:
            condition = np.where(
                np.sqrt(
                    np.power(array_x - origin_x, 2) + np.power(array_y - origin_y, 2)
                )
                <= radius,
                0,
                1.0,
            )
        return (
            np.extract(condition, array_x),
            np.extract(condition, array_y),
            np.extract(condition, array_z),
        )
        # return (x - origin_x**2) + (y - origin_y**2) <= radius

    @staticmethod
    def check_val_in_notch(
        array_x, array_y, array_z, origin_x, xend, length, width, dx_value, angle=60
    ):
        """doc"""
        anglelength = math.sin(angle) * width
        notchend = length + anglelength

        x = np.array([0, notchend, length, xend + dx_value])
        y = np.array([width / 2, width / 2, 0.0, 0.0])

        f = interp1d(x, y)
        plt.scatter(array_x, f(array_x))
        plt.show()
        print(f(array_x))
        condition = np.where(
            np.logical_and(
                array_x <= origin_x + length,
                np.logical_and(array_y <= f(array_x), array_y >= -f(array_x)),
            ),
            0,
            1.0,
        )

        return (
            np.extract(condition, array_x),
            np.extract(condition, array_y),
            np.extract(condition, array_z),
        )
        # return (x - origin_x**2) + (y - origin_y**2) <= radius

    @staticmethod
    def check_val_lower_new(array, limit):
        """doc"""
        return np.where(array <= limit)

    @staticmethod
    def check_val_greater_new(array, limit):
        """doc"""
        return np.where(array >= limit)

    @staticmethod
    def check_val_lower(val, limit):
        """doc"""
        inside = False

        if val <= limit:
            inside = True
        return inside

    @staticmethod
    def check_val_greater(val, limit):
        """doc"""
        inside = False

        if val >= limit:
            inside = True
        return inside

    @staticmethod
    def create_boundary_curve(
        height=0,
        length1=0,
        radius=0,
        length2=0,
        alpha_max=90,
        alpha_max1=90,
        delta_length=0,
        delta_height=0,
    ):
        """doc"""

        dalpha = 0.025
        # print(alpha_max)
        alpha = np.arange(0, alpha_max, dalpha)
        dalpha1 = alpha_max1 / len(alpha)
        if alpha_max1 == 0:
            alpha1 = np.zeros_like(alpha)
        elif alpha_max == alpha_max1:
            alpha1 = np.arange(0, alpha_max, dalpha)
        else:
            alpha1 = np.arange(0, alpha_max1, dalpha1)
        if len(alpha1) > len(alpha):
            alpha1 = np.arange(0, alpha_max1 - dalpha1 / 2, dalpha1)

        ##################################
        # Start
        ##################################
        x_value = np.array([0])
        y_value = np.array([height])
        #########
        # Circle
        #########
        x_value = np.concatenate(
            (x_value, length1 + delta_length + radius * np.sin((-alpha) / 180 * np.pi))
        )
        y_value = np.concatenate(
            (
                y_value,
                height
                - delta_height
                + radius
                - radius * np.cos((-alpha1) / 180 * np.pi),
            )
        )
        #########
        # Circle
        #########

        x_value = np.concatenate(
            (
                x_value,
                length1 + delta_length + length2 + radius * np.sin(alpha / 180 * np.pi),
            )
        )
        y_value = np.concatenate(
            (
                y_value,
                height - delta_height + radius - radius * np.cos(alpha1 / 180 * np.pi),
            )
        )
        #########
        # End
        #########

        x_value = np.concatenate(
            (x_value, np.array([2 * delta_length + 2 * length1 + length2 + 0.01]))
        )
        y_value = np.concatenate((y_value, np.array([height])))

        top_surf = interp1d(x_value, y_value)
        bottom_surf = interp1d(x_value, -y_value)

        return top_surf, bottom_surf

    @staticmethod
    def create_boundary_curve_old(
        height=0,
        length1=0,
        radius=0,
        length2=0,
        alpha_max=90,
        delta_length=0,
        delta_height=0,
    ):
        """doc"""

        dalpha = 0.025
        # print(alpha_max)
        alpha = np.arange(0, alpha_max + dalpha, dalpha)
        ##################################
        # Start
        ##################################
        x_value = np.array([0])
        y_value = np.array([height])
        #########
        # Circle
        #########
        x_value = np.concatenate(
            (x_value, length1 + delta_length + radius * np.sin((-alpha) / 180 * np.pi))
        )
        y_value = np.concatenate(
            (
                y_value,
                height
                + radius
                - delta_height
                - radius * np.cos((-alpha) / 180 * np.pi),
            )
        )
        #########
        # Circle
        #########

        x_value = np.concatenate(
            (
                x_value,
                length1 + delta_length + length2 + radius * np.sin(alpha / 180 * np.pi),
            )
        )
        y_value = np.concatenate(
            (
                y_value,
                height - delta_height + radius - radius * np.cos(alpha / 180 * np.pi),
            )
        )
        #########
        # End
        #########

        x_value = np.concatenate(
            (x_value, np.array([2 * delta_length + 2 * length1 + length2 + 0.01]))
        )
        y_value = np.concatenate((y_value, np.array([height])))

        top_surf = interp1d(x_value, y_value)
        bottom_surf = interp1d(x_value, -y_value)

        # #########
        # # Bottom
        # #########
        # x_value = np.array([2*delta_length+2*length1+length2+0.01])
        # y_value = np.array([0])

        # #########
        # # Circle
        # #########
        # x_value = np.concatenate((x_value,length1+delta_length+length2+radius*np.sin((alpha_max-alpha)/180*np.pi)))
        # #x_value = np.concatenate((x_value,length1+length2+delta_length-radius*np.cos(alpha/180*np.pi)))
        # y_value = np.concatenate((y_value, delta_height -radius + radius*np.cos((alpha_max-alpha)/180*np.pi)))

        # #########
        # # Circle
        # #########
        # x_value = np.concatenate((x_value,length1+delta_length+radius*np.sin(-alpha/180*np.pi)))
        # y_value = np.concatenate((y_value,delta_height -radius +radius*np.cos(-alpha/180*np.pi))) #error
        # #########
        # # End
        # #########
        # x_value = np.concatenate((x_value,np.array([0])))
        # y_value = np.concatenate((y_value,np.array([0])))

        # bottom_surf = interp1d(x_value,y_value)

        return top_surf, bottom_surf
