"""
doc
"""
import csv
import math
import os
from tkinter import Y

import matplotlib.pyplot as plt
import numpy as np

# from sklearn import datasets
# import statsmodels.api as sm
# from patsy import dmatrix
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures

from support.globals import log


class CrackLength:
    @staticmethod
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

        arclength = np.trapz(
            np.sqrt(1 + np.gradient(Y[bounds], X[bounds]) ** 2),
            X[bounds],
        )
        cracklength = arclength

        return cracklength

    def _read_data(data):
        """Extract numpy arrays from a VTK data set."""
        # Go through all arrays, fetch data.
        out = {}
        for k in range(data.GetNumberOfArrays()):
            array = data.GetArray(k)
            if array:
                array_name = array.GetName()
                out[array_name] = vtk.util.numpy_support.vtk_to_numpy(array)

        return out

    def _read_cells(vtk_mesh):
        data = vtk.util.numpy_support.vtk_to_numpy(vtk_mesh.GetCells().GetData())
        offsets = vtk.util.numpy_support.vtk_to_numpy(vtk_mesh.GetCellLocationsArray())
        types = vtk.util.numpy_support.vtk_to_numpy(vtk_mesh.GetCellTypesArray())

        vtk_to_meshio_type = {
            vtk.VTK_VERTEX: "vertex",
            vtk.VTK_LINE: "line",
            vtk.VTK_TRIANGLE: "triangle",
            vtk.VTK_QUAD: "quad",
            vtk.VTK_TETRA: "tetra",
            vtk.VTK_HEXAHEDRON: "hexahedron",
            vtk.VTK_WEDGE: "wedge",
            vtk.VTK_PYRAMID: "pyramid",
        }

        # `data` is a one-dimensional vector with
        # (num_points0, p0, p1, ... ,pk, numpoints1, p10, p11, ..., p1k, ...
        # Translate it into the cells dictionary.
        cells = {}
        for vtk_type, meshio_type in vtk_to_meshio_type.items():
            # Get all offsets for vtk_type
            os = offsets[np.argwhere(types == vtk_type).transpose()[0]]
            num_cells = len(os)
            if num_cells > 0:
                num_pts = data[os[0]]
                # instantiate the array
                arr = np.empty((num_cells, num_pts), dtype=int)
                # sort the num_pts entries after the offsets into the columns
                # of arr
                for k in range(num_pts):
                    arr[:, k] = data[os + k + 1]
                cells[meshio_type] = arr

        return cells

    @staticmethod
    def getCrackLength(username, model_name, output, frequency):
        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")
        print(file)

        reader = vtk.vtkExodusIIReader()
        reader.SetFileName(file)
        vtk_mesh = _read_exodusii_mesh(reader)
        points = vtk.util.numpy_support.vtk_to_numpy(vtk_mesh.GetPoints().GetData())
        cells = CrackLength._read_cells(vtk_mesh)
        point_data = CrackLength._read_data(vtk_mesh.GetPointData())
        cell_data = CrackLength._read_data(vtk_mesh.GetCellData())
        field_data = CrackLength._read_data(vtk_mesh.GetFieldData())

        print(points)
        df = pd.read_csv(file, index_col=0)
        print(df)
        my_array = df.to_numpy()
        print(my_array)

        first_row = True
        time = [my_array[0]]
        # time_string = ''
        Damage = [my_array[1]]
        X = [my_array[2]]
        Y = [my_array[3]]
        Z = [my_array[4]]
        print(time)
        x_min = 28
        x_max = 100
        y_min = -100
        y_max = 100
        # with open(
        #     file,
        #     "r",
        #     encoding="UTF-8",
        # ) as file:
        #     reader = csv.reader(file)
        #     for lines in reader:
        #         if not first_row:
        #             time.append(float(lines[0]))
        #             # time_string+=lines[0]+','
        #             damage_list = []
        #             x_list = []
        #             y_list = []
        #             z_list = []
        #             if lines[1].split(";")[0] != "":
        #                 for idx in range(0, len(lines[1].split(";")) - 1, frequency):

        #                     x_value = float(lines[2].split(";")[idx])
        #                     y_value = float(lines[3].split(";")[idx])
        #                     z_value = float(lines[4].split(";")[idx])

        #                     if x_min <= x_value <= x_max and y_min <= y_value <= y_max:
        #                         x_list.append(x_value)
        #                         y_list.append(y_value)
        #                         z_list.append(z_value)
        #                         damage_list.append(
        #                             float(lines[1].split(";")[idx]) * 100
        #                         )

        #             Damage.append(damage_list)
        #             X.append(x_list)
        #             Y.append(y_list)
        #             Z.append(z_list)
        #         first_row = False

        ############################################
        X_result = []
        Y_result = []
        Crack_length = []
        K1 = []
        for x, y, damage in zip(X, Y, Damage):
            if np.any(x) == False or len(x) < 25:
                continue

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

            # The unweighted model
            regr = LinearRegression()
            poly_reg = PolynomialFeatures(degree=2)
            x_poly = poly_reg.fit_transform(x)
            regr.fit(x_poly, y)
            # plt.plot(
            #     x,
            #     regr.predict(x_poly),
            #     color="green",
            #     linewidth=1,
            #     label="Polynomial weighted model",
            # )
            X_result.append(x)
            Y_result.append(regr.predict(x_poly))
            # plt.scatter(x, y, s=damage)

            # plt.xticks(())
            # plt.yticks(())
            # plt.legend()

            # plt.show()
            # plt.savefig("test.png")

            # arc_length = arclength(X[:, 0], regr.predict(X_poly)[:, 0], 0, 100)
            arc_length = CrackLength.arclength(np.array(x), np.array(regr.predict(x_poly)), 0, 100)
            print(arc_length)
            Crack_length.append(arc_length)

            k1 = CrackLength.calculate_k1(100, 10, 50, arc_length)
            log.info(k1)
            K1.append(k1)

        # plt.plot(range(0, len(Crack_length)), Crack_length)
        # image_file = os.path.join(resultpath, model_name + "_" + output + "_crack.png")
        # plt.savefig(image_file)
        # plt.show
        response = [time, Crack_length, K1]
        return response

    @staticmethod
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
