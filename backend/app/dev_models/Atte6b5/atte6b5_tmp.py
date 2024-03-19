# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d


class CheckVal:
    def __init__(self):
        pass

    def check_val_lower(self, val, limit):
        inside = False

        if val <= limit:
            inside = True
        return inside

    def check_val_greater(self, val, limit):
        inside = False

        if val >= limit:
            inside = True
        return inside

    def create_boundary_curve(
        self,
        height=0,
        length1=0,
        radius=0,
        length2=0,
        alpha_max=90,
        delta_length=0,
        delta_height=0,
    ):
        dalpha = 0.025
        print(alpha_max)
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
            (
                x_value,
                length1 + delta_length + radius * np.sin((-alpha) / 180 * np.pi),
            )
        )
        y_value = np.concatenate(
            (
                y_value,
                height + radius - delta_height - radius * np.cos((-alpha) / 180 * np.pi),
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
            (
                x_value,
                np.array([2 * delta_length + 2 * length1 + length2 + 0.01]),
            )
        )
        y_value = np.concatenate((y_value, np.array([height])))

        top_surf = interp1d(x_value, y_value)

        #########
        # Bottom
        #########
        x_value = np.array([2 * length1 + 2 * delta_length + length2 + 0.1])
        y_value = np.array([0])

        #########
        # Circle
        #########
        x_value = np.concatenate(
            (
                x_value,
                length1 + delta_length + length2 + radius * np.sin((alpha_max - alpha) / 180 * np.pi),
            )
        )
        # x_value = np.concatenate((x_value,length1+length2+delta_length-radius*np.cos(alpha/180*np.pi)))
        y_value = np.concatenate(
            (
                y_value,
                delta_height - radius + radius * np.cos((alpha_max - alpha) / 180 * np.pi),
            )
        )

        #########
        # Circle
        #########
        x_value = np.concatenate(
            (
                x_value,
                length1 + delta_length + radius * np.sin(-alpha / 180 * np.pi),
            )
        )
        y_value = np.concatenate(
            (
                y_value,
                delta_height - radius + radius * np.cos(-alpha / 180 * np.pi),
            )
        )  # error
        #########
        # End
        #########
        x_value = np.concatenate((x_value, np.array([0])))
        y_value = np.concatenate((y_value, np.array([0])))

        bottom_surf = interp1d(x_value, y_value)

        return top_surf, bottom_surf


if __name__ == "__main__":
    c = CheckVal()
    dx_value = 0.001
    t = dx_value
    Lges = 0.115
    print(dx_value)
    dx_value = Lges / int(Lges / dx_value)

    height1 = 0.019
    height2 = 0.013
    dy = height1 / int(height1 / dx_value)

    print(dx_value, dy)
    boundary_condition = 0.002
    radius = 0.076
    length2 = 0.057
    delta_length = np.sqrt(radius * radius - (radius - (height1 - height2) / 2) ** 2)

    length1 = (Lges - 2 * delta_length - length2) / 2
    delta_height = (height1 - height2) / 2
    alpha = np.arccos((radius - delta_height) / radius) * 180 / np.pi

    top_surf, bottom_surf = c.create_boundary_curve(
        height=height1,
        length1=length1,
        radius=radius,
        length2=length2,
        alpha_max=alpha,
        delta_length=delta_length,
        delta_height=delta_height,
    )
    block_def = np.array(
        [
            0,
            boundary_condition,
            length1,
            length1 + 2 * delta_length + length2,
            Lges - boundary_condition,
        ]
    )

    x_value = np.arange(0, Lges + dx_value, dx_value)

    y_value = np.arange(0, height1 + dy, dy)
    z_value = np.arange(0, t, dx_value)
    mat_num = 0
    xList = []
    yList = []
    vol = dx_value * dx_value  # *dx_value
    stringLeft = ""
    stringRight = ""
    string = "# x y z block_id volume\n"
    num = 0
    bccount = 0
    for xval in x_value:
        for yval in y_value:
            for zval in z_value:
                if c.check_val_greater(yval, bottom_surf(xval)) and c.check_val_lower(yval, top_surf(xval)):
                    num += 1
                    for idx, val in enumerate(block_def):
                        if c.check_val_greater(xval, val):
                            mat_num = idx + 1
                    if c.check_val_lower(xval, block_def[0]):
                        stringLeft += str(num) + "\n"
                        bccount += 1
                    if c.check_val_greater(xval, block_def[-1]):
                        stringRight += str(num) + "\n"
                        bccount += 1
                    string += str(xval) + " " + str(yval) + " " + str(zval) + " " + str(mat_num) + " " + str(vol) + "\n"
                    xList.append(xval)
                    yList.append(yval)

    for zval in z_value:
        string += (
            str(length1 + delta_length)
            + " "
            + str(0.5 * (height1 - height2))
            + " "
            + str(zval)
            + " "
            + str(3)
            + " "
            + str(vol)
            + "\n"
        )
    xList.append(length1 + delta_length)
    yList.append(0.5 * (height1 - height2))
    fid = open("dogbone.txt", "w")
    fid.write(string)
    fid.close()

    fid = open("BCleft.txt", "w")
    fid.write(stringLeft)
    fid.close()

    fid = open("BCright.txt", "w")
    fid.write(stringRight)
    fid.close()
    print(
        "numer of Nodes",
        num,
        "horizon 4dx",
        4.01 * dx_value,
        " numer of BC nodes",
        bccount,
    )

    print(np.max(x_value))
    yt = top_surf(x_value)
    yb = bottom_surf(x_value)
    plt.plot(x_value, yt)
    plt.plot(x_value, yb)
    x_value = [length1, length1]
    y_value = [0, height1]
    y2 = [(height1 - height2) / 2, height2 + (height1 - height2) / 2]
    plt.plot(x_value, y_value)
    x_value = [length1 + delta_length, length1 + delta_length]
    plt.plot(x_value, y2)
    x_value = [
        length1 + delta_length + length2,
        length1 + delta_length + length2,
    ]
    plt.plot(x_value, y2)
    x_value = [
        length1 + 2 * delta_length + length2,
        length1 + 2 * delta_length + length2,
    ]
    plt.plot(x_value, y_value)
    plt.plot(xList, yList, "*")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.show()
